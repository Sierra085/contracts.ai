let extractedText = '';

// DOM elements
const uploadForm = document.getElementById('uploadForm');
const chatForm = document.getElementById('chatForm');
const uploadStatus = document.getElementById('uploadStatus');
const textPreview = document.getElementById('textPreview');
const extractedTextEl = document.getElementById('extractedText');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatInputSection = document.getElementById('chatInputSection');
const clearChatBtn = document.getElementById('clearChat');
const riskAnalysisSection = document.getElementById('riskAnalysisSection');
const analyzeRisksBtn = document.getElementById('analyzeRisksBtn');
const riskAnalysisResults = document.getElementById('riskAnalysisResults');
const riskAnalysisContent = document.getElementById('riskAnalysisContent');
const closeRiskAnalysis = document.getElementById('closeRiskAnalysis');
const riskAnalysisPlaceholder = document.getElementById('riskAnalysisPlaceholder');
const unloadFileBtn = document.getElementById('unloadFileBtn');
const exportRisksPdf = document.getElementById('exportRisksPdf');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const progressStatus = document.getElementById('progressStatus');

// Upload form handler
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Please select a file.', 'warning');
        return;
    }
    
    formData.append('file', file);
    
    // Show loading with progress bar
    showProgress(0, 'Preparing to extract text from document...');
    
    // Simulate progress during upload
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        updateProgress(progress, 'Extracting text from document...');
    }, 200);
    
    try {
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        const result = await response.json();
        
        if (response.ok) {
            updateProgress(100, 'Text extraction completed!');
            extractedText = result.text;
            
            setTimeout(() => {
                hideProgress();
                showStatus(`✅ Successfully extracted text from ${file.name}`, 'success');
            }, 500);
            
            // Show text preview
            extractedTextEl.textContent = extractedText.substring(0, 300) + '...';
            textPreview.style.display = 'block';
            
            // Enable chat
            enableChat();
            
            // Show risk analysis button
            riskAnalysisSection.style.display = 'block';
            
            // Show unload button
            unloadFileBtn.style.display = 'block';
            
        } else {
            hideProgress();
            showStatus(`❌ Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        clearInterval(progressInterval);
        hideProgress();
        showStatus(`❌ Error uploading file: ${error.message}`, 'danger');
    }
});

// Chat form handler
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = chatInput.value.trim();
    if (!question) return;
    
    // Add user message
    addMessage(question, 'user');
    
    // Clear input and disable
    chatInput.value = '';
    chatInput.disabled = true;
    sendButton.disabled = true;
    
    // Show AI thinking
    const thinkingId = addMessage('<div class="loading"></div> AI is analyzing...', 'ai');
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: extractedText,
                question: question
            })
        });
        
        const result = await response.json();
        
        // Remove thinking message
        document.getElementById(thinkingId).remove();
        
        if (response.ok) {
            addMessage(result.answer, 'ai');
        } else {
            // Handle different error types with appropriate styling
            let errorClass = 'danger';
            if (response.status === 429) {
                errorClass = 'warning'; // Rate limit - use warning style
            }
            addMessage(`<div class="alert alert-${errorClass} mb-0">${result.error}</div>`, 'ai');
        }
    } catch (error) {
        // Remove thinking message
        document.getElementById(thinkingId).remove();
        addMessage(`<div class="alert alert-danger mb-0">❌ Network Error: ${error.message}</div>`, 'ai');
    }
    
    // Re-enable input
    chatInput.disabled = false;
    sendButton.disabled = false;
    chatInput.focus();
});

// Clear chat handler
clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> Chat cleared. Ask a new question about your document.</div>';
});

// Risk analysis handler
analyzeRisksBtn.addEventListener('click', async () => {
    if (!extractedText) {
        showStatus('Please upload a document first.', 'warning');
        return;
    }
    
    // Disable button and show loading with progress
    analyzeRisksBtn.disabled = true;
    analyzeRisksBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    
    showProgress(0, 'Initializing contract risk analysis...');
    
    // Simulate progress during analysis
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 85) progress = 85;
        
        let statusText = 'Analyzing contract risks...';
        if (progress > 20) statusText = 'Identifying financial risks...';
        if (progress > 40) statusText = 'Evaluating legal compliance...';
        if (progress > 60) statusText = 'Assessing operational risks...';
        if (progress > 80) statusText = 'Generating recommendations...';
        
        updateProgress(progress, statusText);
    }, 300);
    
    try {
        const response = await fetch('/analyze-risks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: extractedText
            })
        });
        
        clearInterval(progressInterval);
        const result = await response.json();
        
        if (response.ok) {
            updateProgress(100, 'Risk analysis completed!');
            
            setTimeout(() => {
                hideProgress();
                displayRiskAnalysis(result.analysis);
                riskAnalysisResults.style.display = 'block';
                riskAnalysisPlaceholder.style.display = 'none';
            }, 500);
        } else {
            hideProgress();
            let errorClass = 'danger';
            if (response.status === 429) {
                errorClass = 'warning';
            }
            showStatus(`<div class="alert alert-${errorClass} mb-0">${result.error}</div>`, errorClass);
        }
    } catch (error) {
        clearInterval(progressInterval);
        hideProgress();
        showStatus(`<div class="alert alert-danger mb-0">❌ Network Error: ${error.message}</div>`, 'danger');
    }
    
    // Re-enable button
    analyzeRisksBtn.disabled = false;
    analyzeRisksBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Analyze Contract Risks';
});

// Close risk analysis handler
closeRiskAnalysis.addEventListener('click', () => {
    riskAnalysisResults.style.display = 'none';
    riskAnalysisPlaceholder.style.display = 'block';
});

// Export risks to PDF handler
exportRisksPdf.addEventListener('click', () => {
    exportRiskAnalysisToPDF();
});

// Unload file handler
unloadFileBtn.addEventListener('click', () => {
    // Confirm before unloading
    if (confirm('Are you sure you want to unload the file and reset everything? This will clear all content and chat history.')) {
        resetApplication();
    }
});

// Helper function to reset the entire application
function resetApplication() {
    // Clear extracted text
    extractedText = '';
    
    // Reset file input
    document.getElementById('file').value = '';
    
    // Hide unload button
    unloadFileBtn.style.display = 'none';
    
    // Clear and hide text preview
    extractedTextEl.textContent = '';
    textPreview.style.display = 'none';
    
    // Hide risk analysis section
    riskAnalysisSection.style.display = 'none';
    
    // Reset chat
    chatMessages.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> 
            Upload a document to start chatting with AI about its contents.
            <br><small class="text-muted mt-1 d-block">
                <i class="fas fa-clock"></i> Using Gemini API free tier - if you hit rate limits, please wait a few minutes.
            </small>
        </div>
    `;
    
    // Disable chat input
    chatInputSection.style.display = 'none';
    chatInput.disabled = true;
    sendButton.disabled = true;
    chatInput.value = '';
    
    // Close and reset risk analysis
    riskAnalysisResults.style.display = 'none';
    riskAnalysisPlaceholder.style.display = 'block';
    riskAnalysisContent.innerHTML = '';
    currentRiskAnalysis = null; // Clear stored analysis data
    
    // Clear upload status
    uploadStatus.innerHTML = '';
    
    // Hide progress bar
    hideProgress();
    
    // Show success message
    showStatus('✅ Application reset successfully. You can now upload a new document.', 'success');
}

// Helper functions
function showStatus(message, type) {
    uploadStatus.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
}

function enableChat() {
    chatMessages.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> Document loaded! Ask me anything about its contents.</div>';
    chatInputSection.style.display = 'block';
    chatInput.disabled = false;
    sendButton.disabled = false;
    chatInput.focus();
}

function displayRiskAnalysis(analysis) {
    // Store the analysis data for PDF export
    currentRiskAnalysis = analysis;
    
    let html = '';
    
    if (analysis.raw_analysis) {
        // If we couldn't parse JSON, show raw analysis
        html = `<div class="alert alert-info">
            <h6>Risk Analysis:</h6>
            <pre style="white-space: pre-wrap;">${analysis.raw_analysis}</pre>
        </div>`;
    } else {
        // Display structured analysis
        const riskLevelClass = getRiskLevelClass(analysis.overall_risk_level);
        
        html = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="alert alert-${riskLevelClass}">
                        <h6><i class="fas fa-shield-alt"></i> Overall Risk Level</h6>
                        <strong>${analysis.overall_risk_level || 'Unknown'}</strong>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-chart-bar"></i> Risk Categories Found</h6>
                        <strong>${analysis.risk_categories ? analysis.risk_categories.length : 0}</strong>
                    </div>
                </div>
            </div>
        `;
        
        if (analysis.key_concerns && analysis.key_concerns.length > 0) {
            html += `
                <div class="alert alert-warning mb-3">
                    <h6><i class="fas fa-exclamation-triangle"></i> Key Concerns</h6>
                    <ul class="mb-0">
                        ${analysis.key_concerns.map(concern => `<li>${concern}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (analysis.risk_categories && analysis.risk_categories.length > 0) {
            html += '<h6><i class="fas fa-list"></i> Risk Categories</h6>';
            analysis.risk_categories.forEach(category => {
                const categoryClass = getRiskLevelClass(category.level);
                html += `
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <span class="badge bg-${categoryClass}">${category.level || 'Unknown'}</span>
                                ${category.category || 'Unknown Category'}
                            </h6>
                        </div>
                        <div class="card-body">
                            <p>${category.description || 'No description available'}</p>
                            
                            ${category.specific_clauses && category.specific_clauses.length > 0 ? `
                                <h6>Specific Clauses:</h6>
                                <ul>
                                    ${category.specific_clauses.map(clause => `<li><small>${clause}</small></li>`).join('')}
                                </ul>
                            ` : ''}
                            
                            ${category.recommendations && category.recommendations.length > 0 ? `
                                <h6>Recommendations:</h6>
                                <ul class="text-success">
                                    ${category.recommendations.map(rec => `<li><small>${rec}</small></li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
        }
        
        if (analysis.missing_protections && analysis.missing_protections.length > 0) {
            html += `
                <div class="alert alert-danger mb-3">
                    <h6><i class="fas fa-shield-alt"></i> Missing Protections</h6>
                    <ul class="mb-0">
                        ${analysis.missing_protections.map(protection => `<li>${protection}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (analysis.summary) {
            html += `
                <div class="alert alert-secondary">
                    <h6><i class="fas fa-clipboard-list"></i> Summary</h6>
                    <p class="mb-0">${analysis.summary}</p>
                </div>
            `;
        }
    }
    
    riskAnalysisContent.innerHTML = html;
}

function getRiskLevelClass(level) {
    if (!level) return 'secondary';
    switch (level.toLowerCase()) {
        case 'low': return 'success';
        case 'medium': return 'warning';
        case 'high': return 'danger';
        default: return 'secondary';
    }
}

function addMessage(content, sender) {
    const messageId = 'msg-' + Date.now();
    const isUser = sender === 'user';
    const icon = isUser ? 'fas fa-user' : 'fas fa-robot';
    const className = isUser ? 'user-message' : 'ai-message';
    const title = isUser ? 'You' : 'AI Assistant';
    
    const messageHtml = `
        <div id="${messageId}" class="message ${className}">
            <div class="message-header">
                <i class="${icon}"></i>
                <strong>${title}:</strong>
            </div>
            <div>${content}</div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', messageHtml);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Auto-focus on chat input when enabled
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Progress bar functions
function showProgress(percentage, status) {
    progressContainer.style.display = 'block';
    updateProgress(percentage, status);
}

function updateProgress(percentage, status) {
    percentage = Math.min(100, Math.max(0, percentage));
    progressBar.style.width = percentage + '%';
    progressText.textContent = Math.round(percentage) + '%';
    progressStatus.textContent = status;
    
    // Change color based on progress
    progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
    if (percentage >= 100) {
        progressBar.classList.add('bg-success');
    } else if (percentage >= 50) {
        progressBar.classList.add('bg-info');
    } else {
        progressBar.classList.add('bg-primary');
    }
}

function hideProgress() {
    setTimeout(() => {
        progressContainer.style.display = 'none';
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        progressStatus.textContent = '';
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
    }, 100);
}

// Global variable to store current risk analysis data for PDF export
let currentRiskAnalysis = null;

// PDF Export function
function exportRiskAnalysisToPDF() {
    if (!currentRiskAnalysis) {
        alert('No risk analysis data available to export.');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Set up the document
    doc.setFontSize(20);
    doc.text('Contract Risk Analysis Report', 20, 20);
    
    doc.setFontSize(12);
    let y = 40;
    
    // Add timestamp
    const date = new Date().toLocaleString();
    doc.text(`Generated on: ${date}`, 20, y);
    y += 20;
    
    if (currentRiskAnalysis.raw_analysis) {
        // Handle raw analysis
        doc.text('Risk Analysis:', 20, y);
        y += 10;
        
        const lines = doc.splitTextToSize(currentRiskAnalysis.raw_analysis, 170);
        doc.text(lines, 20, y);
    } else {
        // Handle structured analysis
        if (currentRiskAnalysis.overall_risk_level) {
            doc.setFontSize(14);
            doc.text(`Overall Risk Level: ${currentRiskAnalysis.overall_risk_level}`, 20, y);
            y += 15;
        }
        
        if (currentRiskAnalysis.key_concerns && currentRiskAnalysis.key_concerns.length > 0) {
            doc.setFontSize(12);
            doc.text('Key Concerns:', 20, y);
            y += 10;
            
            currentRiskAnalysis.key_concerns.forEach(concern => {
                const lines = doc.splitTextToSize(`• ${concern}`, 170);
                doc.text(lines, 25, y);
                y += lines.length * 5;
            });
            y += 10;
        }
        
        if (currentRiskAnalysis.risk_categories && currentRiskAnalysis.risk_categories.length > 0) {
            doc.text('Risk Categories:', 20, y);
            y += 10;
            
            currentRiskAnalysis.risk_categories.forEach(category => {
                // Check if we need a new page
                if (y > 250) {
                    doc.addPage();
                    y = 20;
                }
                
                doc.setFontSize(11);
                doc.text(`${category.category || 'Unknown'} - Level: ${category.level || 'Unknown'}`, 25, y);
                y += 8;
                
                if (category.description) {
                    const descLines = doc.splitTextToSize(category.description, 160);
                    doc.text(descLines, 25, y);
                    y += descLines.length * 5 + 5;
                }
                
                if (category.recommendations && category.recommendations.length > 0) {
                    doc.text('Recommendations:', 25, y);
                    y += 6;
                    
                    category.recommendations.forEach(rec => {
                        const recLines = doc.splitTextToSize(`• ${rec}`, 155);
                        doc.text(recLines, 30, y);
                        y += recLines.length * 4;
                    });
                }
                y += 10;
            });
        }
        
        if (currentRiskAnalysis.missing_protections && currentRiskAnalysis.missing_protections.length > 0) {
            if (y > 240) {
                doc.addPage();
                y = 20;
            }
            
            doc.text('Missing Protections:', 20, y);
            y += 10;
            
            currentRiskAnalysis.missing_protections.forEach(protection => {
                const lines = doc.splitTextToSize(`• ${protection}`, 170);
                doc.text(lines, 25, y);
                y += lines.length * 5;
            });
            y += 10;
        }
        
        if (currentRiskAnalysis.summary) {
            if (y > 240) {
                doc.addPage();
                y = 20;
            }
            
            doc.text('Summary:', 20, y);
            y += 10;
            
            const summaryLines = doc.splitTextToSize(currentRiskAnalysis.summary, 170);
            doc.text(summaryLines, 20, y);
        }
    }
    
    // Save the PDF
    const filename = `contract-risk-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(filename);
}
