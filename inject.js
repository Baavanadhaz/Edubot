document.addEventListener('DOMContentLoaded', () => {
    const voiceAgentContainer = document.getElementById('voice-agent-container');
    voiceAgentContainer.innerHTML = `
        <div id="voice-agent" class="voice-agent">
            <div class="voice-agent-header">Skadoosh EduBot</div>
            <div id="chat-body" class="voice-agent-body">
                <!-- Chat bubbles will be inserted here -->
            </div>
            
            <!-- New element for live transcript -->
            <div id="live-transcript-container" class="live-transcript-container">
                <span id="live-transcript"></span>
            </div>

            <div class="voice-agent-footer">
                <div id="status-indicator" class="status-indicator">Connecting...</div>
                <div class="controls">
                    <button id="start-call-button" class="control-button" title="Start Speaking">
                        <i class="fas fa-phone"></i>
                    </button>
                    <button id="end-call-button" class="control-button" title="End Conversation">
                        <i class="fas fa-phone-slash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
});