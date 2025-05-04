document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded - starting initialization');
    
    // Parse URL to get token
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    console.log('Token from URL:', token);
    
    let currentToken = token;
    
    // DOM elements - log if found or not for debugging
    const messagesContainer = document.getElementById('messages');
    console.log('Messages container found:', !!messagesContainer);
    
    const questionInput = document.getElementById('question-input');
    const askButton = document.getElementById('ask-button');
    const statusElement = document.getElementById('status');
    const statusIndicator = document.getElementById('status-indicator');
    const documentsContainer = document.getElementById('documents-container');
    const documentModal = document.getElementById('document-modal');
    const modalDocumentTitle = document.getElementById('modal-document-title');
    const documentContentDisplay = document.getElementById('document-content-display');
    
    // Function to check if this is the user's first visit
    async function checkFirstTimeUser() {
        try {
            console.log('[checkFirstTimeUser] Starting with token:', token);
            
            if (!token) {
                console.log('[checkFirstTimeUser] No token provided');
                return;
            }
            
            // Get customer info
            console.log('[checkFirstTimeUser] Fetching customer info from API');
            const infoResponse = await fetch(`/api/token/info?token=${token}`);
            const customerInfo = await infoResponse.json();
            
            // Get interaction count
            console.log('[checkFirstTimeUser] Fetching interaction count from API');
            const countResponse = await fetch(`/api/interactions/count?token=${token}`);
            const countData = await countResponse.json();
            
            console.log('[checkFirstTimeUser] Customer info:', customerInfo);
            console.log('[checkFirstTimeUser] Interaction count data:', countData);
            
            // If this is the first time (count is 0) and we have a customer name, show welcome message
            if (countData.count === 0 && customerInfo.customer_name) {
                console.log('[checkFirstTimeUser] First time user! Adding welcome message for:', customerInfo.customer_name);
                
                // Create welcome message with customer name
                const welcomeMessage = `Welcome, ${customerInfo.customer_name}! I'm your AI assistant. How can I help you today?`;
                console.log('[checkFirstTimeUser] Welcome message created:', welcomeMessage);
                
                // Add welcome message to chat (after the initial greeting)
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                messageDiv.textContent = welcomeMessage;
                
                // Add time element
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = getCurrentTime();
                messageDiv.appendChild(timeDiv);
                
                console.log('[checkFirstTimeUser] Appending message to container:', messagesContainer);
                messagesContainer.appendChild(messageDiv);
                
                // Scroll to the bottom of the messages container
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                console.log('[checkFirstTimeUser] Welcome message added successfully');
            } else {
                console.log('[checkFirstTimeUser] Not a first-time user or no customer name');
            }
        } catch (error) {
            console.error('[checkFirstTimeUser] Error:', error);
        }
    }
    
    // Function to format current time
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0' + minutes : minutes;
        
        return hours + ':' + minutes + ' ' + ampm;
    }
    
    // Function to add a message to the chat
    function addMessage(text, isUser) {
        console.log('[addMessage] Adding message:', { text, isUser });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        // Add message text
        messageDiv.textContent = text;
        
        // Add time element
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();
        messageDiv.appendChild(timeDiv);
        
        console.log('[addMessage] Appending to container:', messagesContainer);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to the bottom of the messages container
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        console.log('[addMessage] Message added successfully');
    }
    
    // Function to add a loading message
    function addLoadingMessage() {
        console.log('[addLoadingMessage] Adding loading message');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading';
        loadingDiv.id = 'loading-message';
        
        const loadingText = document.createElement('span');
        loadingText.textContent = 'Thinking';
        
        const dotsContainer = document.createElement('div');
        dotsContainer.className = 'loading-dots';
        
        for (let i = 0; i < 3; i++) {
            const dotSpan = document.createElement('span');
            dotsContainer.appendChild(dotSpan);
        }
        
        loadingDiv.appendChild(loadingText);
        loadingDiv.appendChild(dotsContainer);
        
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Function to remove the loading message
    function removeLoadingMessage() {
        console.log('[removeLoadingMessage] Removing loading message');
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
            console.log('[removeLoadingMessage] Loading message removed');
        } else {
            console.log('[removeLoadingMessage] No loading message found to remove');
        }
    }


        

    // Function to check for first-time user and add welcome message to chat
    async function checkFirstTimeUserAndAddMessage() {
        try {
            console.log('[checkFirstTimeUserAndAddMessage] Starting with token:', token);
            
            if (!token) {
                console.log('[checkFirstTimeUserAndAddMessage] No token available');
                return;
            }
            
            // Get the interaction count
            console.log('[checkFirstTimeUserAndAddMessage] Fetching interaction count');
            const countResponse = await fetch(`/api/interactions/count?token=${token}`);
            if (!countResponse.ok) {
                console.error('[checkFirstTimeUserAndAddMessage] Error checking interaction count:', countResponse.status, countResponse.statusText);
                return;
            }
            
            const countData = await countResponse.json();
            console.log('[checkFirstTimeUserAndAddMessage] Interaction count data:', countData);
            
            // Check if user has reached limit
            if (countData.count >= 5) {
                console.log('[checkFirstTimeUserAndAddMessage] User has reached interaction limit');
                return; // Don't add welcome message for expired users
            }
            
            // Get customer info
            console.log('[checkFirstTimeUserAndAddMessage] Fetching customer info');
            const infoResponse = await fetch(`/api/token/info?token=${token}`);
            if (!infoResponse.ok) {
                console.error('[checkFirstTimeUserAndAddMessage] Error fetching customer info:', infoResponse.status, infoResponse.statusText);
                return;
            }
            
            const customerInfo = await infoResponse.json();
            console.log('[checkFirstTimeUserAndAddMessage] Customer info:', customerInfo);
            
            // If this is the first time (count is 0) and we have a customer name, add welcome message to chat
            if (countData.count === 0 && customerInfo.customer_name) {
                console.log('[checkFirstTimeUserAndAddMessage] First time user! Creating welcome message for:', customerInfo.customer_name);
                
                // Create welcome message with customer name
                const welcomeMessage = `Welcome, ${customerInfo.customer_name}! I'm your AI assistant. How can I help you today?`;
                
                // Add message to chat
                console.log('[checkFirstTimeUserAndAddMessage] Adding welcome message to chat:', welcomeMessage);
                addMessage(welcomeMessage, false);
                console.log('[checkFirstTimeUserAndAddMessage] Welcome message successfully added');
            } else {
                console.log('[checkFirstTimeUserAndAddMessage] Not a first-time user or no customer name. Count:', countData.count, 'Name:', customerInfo.customer_name);
            }
        } catch (error) {
            console.error('[checkFirstTimeUserAndAddMessage] Error:', error);
        }
    }
    
    // Function to check interaction limit
    async function checkInteractionLimit(token) {
        try {
            console.log('[checkInteractionLimit] Checking for token:', token);
            
            if (!token) {
                console.log('[checkInteractionLimit] No token provided');
                return false;
            }
            
            // Create a new endpoint in routes.py to get the interaction count for a token
            const response = await fetch(`/api/interactions/count?token=${token}`);
            console.log('[checkInteractionLimit] Response status:', response.status);
            
            if (!response.ok) {
                console.error('[checkInteractionLimit] Error:', response.statusText);
                return false;
            }
            
            const data = await response.json();
            console.log('[checkInteractionLimit] Count data:', data);
            
            // If interaction count is 4 or more, show limit popup
            if (data.count >= 5) {
                console.log('[checkInteractionLimit] Limit reached! Showing popup');
                showLimitReachedPopup();
                return true;
            } else {
                console.log(`[checkInteractionLimit] Limit not reached: ${data.count}/4 interactions used`);
                return false;
            }
        } catch (error) {
            console.error('[checkInteractionLimit] Error:', error);
            return false;
        }
    }
    
    // Function to show the limit reached popup
    function showLimitReachedPopup() {
        console.log('[showLimitReachedPopup] Creating and showing popup');
        // Create popup if it doesn't exist yet
        if (!document.getElementById('limit-popup')) {
            const popupDiv = document.createElement('div');
            popupDiv.id = 'limit-popup';
            popupDiv.className = 'popup';
            popupDiv.style.display = 'block';
            
            popupDiv.innerHTML = `
                <div class="popup-content">
                    <h2 class="welcome-title">Interaction Limit Reached</h2>
                    <div class="welcome-highlight">
                        <p>You have reached the maximum number of interactions (4) for this demo.</p>
                        <p>Please contact us to learn more about our premium plans with unlimited interactions.</p>
                    </div>
                    <a href="https://www.finitx.com/contact-us/" class="welcome-button" style="text-decoration: none; display: inline-block; margin-top: 20px;" target="_blank">
                        Contact Sales
                    </a>
                </div>
            `;
            
            document.body.appendChild(popupDiv);
            console.log('[showLimitReachedPopup] Popup created and added to document');
            
            // Disable the chat interface
            questionInput.disabled = true;
            askButton.disabled = true;
            
            // Add a message to the chat
            addMessage("You've reached the maximum number of interactions for this demo. Please contact our sales team for a full version with unlimited interactions.", false);
        } else {
            console.log('[showLimitReachedPopup] Popup already exists');
        }
    }
    





    // Function to ask a question
    async function askQuestion() {
        const question = questionInput.value.trim();
        console.log('[askQuestion] Question:', question);
        
        if (!question) {
            console.log('[askQuestion] Empty question, returning');
            return;
        }
        
        // Check interaction limit before processing
        if (token) {
            console.log('[askQuestion] Checking interaction limit');
            const limitReached = await checkInteractionLimit(token);
            if (limitReached) {
                console.log('[askQuestion] Limit reached - question will not be processed');
                return; // Don't process the question if limit is reached
            }
        }
        
        console.log('[askQuestion] Proceeding with question');
        
        // Add the user's question to the chat
        addMessage(question, true);
        
        // Clear the input field
        questionInput.value = '';
        
        // Show loading indicator
        addLoadingMessage();
        
        try {
            // Get the token from the URL again just to be safe
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            console.log('[askQuestion] Using token for API call:', token);
            
            // Prepare the API URL with token
            let apiUrl = '/api/ask';
            if (token) {
                apiUrl += `?token=${token}`;
            }
            
            console.log('[askQuestion] Sending request to:', apiUrl);
            // Send the question to the API
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });
            
            console.log('[askQuestion] Response status:', response.status);
            
            // Remove loading indicator
            removeLoadingMessage();
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'API request failed');
            }
            
            const data = await response.json();
            console.log('[askQuestion] Answer received:', data.answer);
            
            // Add the bot's response to the chat
            addMessage(data.answer, false);
            
            // Check limit again after the interaction is recorded
            if (token) {
                console.log('[askQuestion] Checking interaction limit after response');
                setTimeout(() => checkInteractionLimit(token), 3000); // Small delay to ensure interaction is recorded
            }
        } catch (error) {
            console.error('[askQuestion] Error:', error);
            
            // Remove loading indicator
            removeLoadingMessage();
            
            // Add an error message to the chat
            addMessage(`I'm sorry, I encountered an error: ${error.message || 'Unknown error occurred'}. Please try again.`, false);
        }
    }
    











    
    // Event listener for the ask button
    askButton.addEventListener('click', function() {
        console.log('[eventListener] Ask button clicked');
        askQuestion();
    });
    
    // Event listener for pressing Enter in the input field
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            console.log('[eventListener] Enter key pressed in input field');
            askQuestion();
        }
    });
    
    // Check if the API is available
    async function checkHealth() {
        try {
            console.log('[checkHealth] Checking API health');
            const response = await fetch('/api/health');
            if (response.ok) {
                console.log('[checkHealth] API health check successful');
                statusElement.textContent = 'Connected';
                statusIndicator.className = 'status-indicator status-connected';
                return true;
            } else {
                console.log('[checkHealth] API health check failed');
                statusElement.textContent = 'API Error';
                statusIndicator.className = 'status-indicator status-error';
                return false;
            }
        } catch (error) {
            console.error('[checkHealth] Health check error:', error);
            statusElement.textContent = 'Connection Failed';
            statusIndicator.className = 'status-indicator status-error';
            return false;
        }
    }

    // Initialize the page
    async function initPage() {
        console.log('[initPage] Starting page initialization');
        
        // Check API health
        console.log('[initPage] Checking API health');
        await checkHealth();
        
        // Load documents
        console.log('[initPage] Loading knowledge documents');
        await loadKnowledgeDocuments();
        
        // Important: Removing the call to checkFirstTimeUser() from here
        // We'll rely only on the separate timeout call to checkFirstTimeUserAndAddMessage
        
        // Check interaction limit
        if (token) {
            console.log('[initPage] Setting timeout for interaction limit check');
            setTimeout(() => checkInteractionLimit(token), 1000);
        }
        
        console.log('[initPage] Page initialization complete');
    }
    
    // Function to load document cards
    async function loadKnowledgeDocuments() {
        try {
            console.log('[loadKnowledgeDocuments] Starting to load documents');
            // Show loading state
            documentsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 20px;">
                    <p>Loading documents...</p>
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            
            // Fetch documents from API
            console.log('[loadKnowledgeDocuments] Fetching from API');
            const response = await fetch('/api/documents');
            
            if (!response.ok) {
                throw new Error('Failed to fetch documents');
            }
            
            const data = await response.json();
            const documents = data.documents;
            console.log('[loadKnowledgeDocuments] Documents fetched:', documents.length);
            
            // Clear the container
            documentsContainer.innerHTML = '';
            
            // Add each document card
            documents.forEach(doc => {
                // Create document card
                const docCard = document.createElement('div');
                docCard.className = 'document-card';
                
                // Set icon based on document type
                let iconClass = 'fas fa-file-alt';
                if (doc.type === 'pdf') iconClass = 'fas fa-file-pdf';
                else if (doc.type === 'excel') iconClass = 'fas fa-file-excel';
                else if (doc.type === 'word') iconClass = 'fas fa-file-word';
                
                docCard.innerHTML = `
                    <div class="document-icon">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="document-title">${doc.title}</div>
                    <div class="document-description">${doc.description}</div>
                    <div class="document-size">${doc.size}</div>
                    <div class="document-download">
                        <a href="/data/${doc.filename}" class="download-button" download>
                            <i class="fas fa-download"></i> Download
                        </a>
                        <button class="view-button" data-document-id="${doc.id}" data-filename="${doc.filename}" data-type="${doc.type}" data-title="${doc.title}">
                            <i class="fas fa-eye"></i> Preview
                        </button>
                    </div>
                `;
                
                documentsContainer.appendChild(docCard);
            });
            
            console.log('[loadKnowledgeDocuments] Adding event listeners to view buttons');
            // Add event listeners to view buttons
            document.querySelectorAll('.view-button').forEach(button => {
                button.addEventListener('click', function() {
                    const docId = this.getAttribute('data-document-id');
                    const filename = this.getAttribute('data-filename');
                    const type = this.getAttribute('data-type');
                    const title = this.getAttribute('data-title');
                    
                    viewDocument(docId, filename, type, title);
                });
            });
            
            // If no documents are available
            if (documents.length === 0) {
                console.log('[loadKnowledgeDocuments] No documents found');
                documentsContainer.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #666;">
                        <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 10px; color: var(--primary-color);"></i>
                        <p>No knowledge base documents are currently available.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[loadKnowledgeDocuments] Error:', error);
            documentsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #666;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px; color: #f44336;"></i>
                    <p>Error loading documents. Please try again later.</p>
                </div>
            `;
        }
    }
    
    // Function to view document content
    async function viewDocument(docId, filename, type, title) {
        console.log('[viewDocument] Viewing document:', { docId, filename, type, title });
        try {
            // Set the modal title
            modalDocumentTitle.textContent = title;
            
            // Show loading indicator
            documentContentDisplay.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <p>Loading document content...</p>
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            
            // Show the modal
            documentModal.style.display = 'block';
            
            // Fetch the document content
            console.log('[viewDocument] Fetching document content');
            const response = await fetch(`/data/${filename}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch document content');
            }
            
            // Handle different file types
            if (type === 'pdf') {
                console.log('[viewDocument] Creating PDF embed');
                // For PDFs, we'll create an embed element
                documentContentDisplay.innerHTML = `
                    <div style="height: 100%; width: 100%;">
                        <embed 
                            src="/data/${filename}" 
                            type="application/pdf"
                            width="100%" 
                            height="100%"
                            style="border: none;"
                        >
                    </div>
                `;
            } else {
                console.log('[viewDocument] Displaying text content');
                // For text files, display the content directly
                const content = await response.text();
                documentContentDisplay.textContent = content;
            }
        } catch (error) {
            console.error('[viewDocument] Error:', error);
            documentContentDisplay.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #f44336;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>Error loading document content: ${error.message}</p>
                    <p>Try downloading the file instead.</p>
                </div>
            `;
        }
    }
    
    // Close document modal when clicking the X
    const closeModalBtn = document.querySelector('.close-modal');
    if (closeModalBtn) {
        console.log('[setup] Adding close event to modal X button');
        closeModalBtn.onclick = function() {
            documentModal.style.display = 'none';
        }
    } else {
        console.log('[setup] Warning: Close modal button not found');
    }
    
    // Close document modal when clicking outside the modal
    window.onclick = function(event) {
        if (event.target == documentModal) {
            console.log('[setup] Closing modal from outside click');
            documentModal.style.display = 'none';
        }
    }
    
    console.log('[setup] Setting up welcome message check');
    // Check if first-time user - THIS IS THE KEY PART!
    if (token) {
        console.log('[setup] Token found. Setting timeout for welcome message');
        // Delay the check slightly to ensure the page is fully loaded
        setTimeout(function() {
            console.log('[setup] Timeout fired - checking first-time user');
            checkFirstTimeUserAndAddMessage();
        }, 1000);
    } else {
        console.log('[setup] No token found, skipping welcome message check');
    }
    
    console.log('[setup] Starting page initialization');
    // Initialize the page
    initPage();
    
    console.log('[setup] Setting up health check interval');
    // Periodically check health
    setInterval(checkHealth, 30000);
    
    console.log('[setup] DOM initialization completed');
});