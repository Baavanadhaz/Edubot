document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const micButton = document.getElementById('mic-button');
    const voiceAgent = document.getElementById('voice-agent');
    const startCallButton = document.getElementById('start-call-button');
    const endCallButton = document.getElementById('end-call-button');
    const chatBody = document.getElementById('chat-body');
    const statusIndicator = document.getElementById('status-indicator');
    const liveTranscript = document.getElementById('live-transcript');

    // --- State Variables ---
    let isRecording = false;
    let mediaRecorder;
    let socket;
    let audioProcessor;
    let sessionId = 'session_' + Date.now();
    let currentAudio = null;

    // --- Event Listeners ---
    micButton.addEventListener('click', toggleVoiceAgent);
    startCallButton.addEventListener('click', handleStartCall);
    endCallButton.addEventListener('click', () => toggleVoiceAgent(false));

    // --- Core Functions ---
    function toggleVoiceAgent(show) {
        const shouldShow = show !== undefined ? show : !voiceAgent.classList.contains('active');
        if (shouldShow) {
            voiceAgent.classList.add('active');
            startConversation();
        } else {
            voiceAgent.classList.remove('active');
            resetConversation();
        }
    }

    function startConversation() {
        updateStatus('Getting ready...');
        fetch('/greet', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                addMessageToChat('assistant', data.text);
                playAudioFromBase64(data.audio);
            })
            .catch(error => {
                console.error('Error starting conversation:', error);
                updateStatus('Error. Please try again.');
            });
    }

    function handleStartCall() {
        if (currentAudio) currentAudio.pause();
        if (!isRecording) startStreaming();
        else stopStreaming();
    }

    /**
     * Starts the WebSocket connection and audio streaming process.
     */
    async function startStreaming() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioContext = new AudioContext({ sampleRate: 16000 });
            const source = audioContext.createMediaStreamSource(stream);
            
            // This script processor is a bit old, but has the best browser support.
            // For production, consider using an AudioWorklet.
            audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
            
            audioProcessor.onaudioprocess = (event) => {
                const inputData = event.inputBuffer.getChannelData(0);
                const downsampledData = convertTo16BitPCM(inputData);
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(downsampledData);
                }
            };
            
            source.connect(audioProcessor);
            audioProcessor.connect(audioContext.destination);

            // Connect to the backend WebSocket
            socket = new WebSocket('ws://localhost:5001/listen');
            
            socket.onopen = () => {
                isRecording = true;
                updateStatus('Listening...');
                startCallButton.innerHTML = '<i class="fas fa-stop"></i>';
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.transcript) {
                    liveTranscript.textContent = data.transcript;
                    if (data.is_final) {
                        stopStreaming(); // VAD detected silence
                        processFinalTranscript(data.transcript);
                    }
                }
            };

            socket.onclose = () => {
                console.log('WebSocket closed.');
                isRecording = false;
            };

            socket.onerror = (error) => {
                console.error('WebSocket Error:', error);
                updateStatus('Connection error.');
                isRecording = false;
            };

        } catch (error) {
            console.error("Microphone access error:", error);
            updateStatus("Mic access denied.");
        }
    }

    /**
     * Stops the streaming process and closes connections.
     */
    function stopStreaming() {
        if (!isRecording) return;
        isRecording = false;
        
        if (audioProcessor) {
            audioProcessor.disconnect();
            audioProcessor = null;
        }
        if (socket) {
            socket.close();
            socket = null;
        }
        
        updateStatus('Thinking...');
        startCallButton.innerHTML = '<i class="fas fa-phone"></i>';
        startCallButton.disabled = true;
    }

    /**
     * Sends the final transcript to the backend to get an LLM response.
     * @param {string} transcript The final recognized text.
     */
    function processFinalTranscript(transcript) {
        liveTranscript.textContent = ''; // Clear live transcript
        addMessageToChat('user', transcript);

        fetch('/respond', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: transcript, session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            addMessageToChat('assistant', data.ai_text);
            playAudioFromBase64(data.ai_audio);
        })
        .catch(error => {
            console.error('Error getting response:', error);
            updateStatus('Sorry, an error occurred.');
            startCallButton.disabled = false;
        });
    }

    // --- Helper Functions --- (playAudioFromBase64, addMessageToChat, etc. remain the same)
    function playAudioFromBase64(base64String) {
        const audioBytes = atob(base64String);
        const audioBuffer = new Uint8Array(audioBytes.length);
        for (let i = 0; i < audioBytes.length; i++) audioBuffer[i] = audioBytes.charCodeAt(i);
        const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (currentAudio) currentAudio.pause();
        currentAudio = new Audio(audioUrl);
        updateStatus('Speaking...');
        currentAudio.play();
        currentAudio.onended = () => {
            updateStatus('Ready to listen.');
            startCallButton.disabled = false;
            currentAudio = null;
        };
    }

    function addMessageToChat(role, text) {
        const bubble = document.createElement('div');
        bubble.classList.add('chat-bubble', role);
        bubble.textContent = text;
        chatBody.appendChild(bubble);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function updateStatus(text) {
        statusIndicator.textContent = text;
    }

    function resetConversation() {
        chatBody.innerHTML = '';
        liveTranscript.textContent = '';
        sessionId = 'session_' + Date.now();
        startCallButton.disabled = false;
        if (currentAudio) currentAudio.pause();
        if (isRecording) stopStreaming();
    }

    // Helper to convert float audio to 16-bit PCM for Deepgram
    function convertTo16BitPCM(input) {
        const output = new Int16Array(input.length);
        for (let i = 0; i < input.length; i++) {
            const s = Math.max(-1, Math.min(1, input[i]));
            output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return output.buffer;
    }
});