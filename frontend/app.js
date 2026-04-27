document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const uploadBtn = document.getElementById("upload-btn");
    const uploadStatus = document.getElementById("upload-status");
    const queryForm = document.getElementById("query-form");
    const queryInput = document.getElementById("query-input");
    const chatWindow = document.getElementById("chat-window");
    const streamToggle = document.getElementById("stream-toggle");
    const historyContainer = document.getElementById("history-container");
    const emptyChatMsg = document.getElementById("empty-chat-msg");
    const clearDbBtn = document.getElementById("clear-db-btn");
    const clearHistoryBtn = document.getElementById("clear-history-btn");
    const sourceModalBody = document.getElementById("source-modal-body");

    // Initialize Marked.js
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // --- History Loading ---
    async function loadHistory() {
        try {
            const res = await fetch("/api/history");
            const history = await res.json();
            historyContainer.innerHTML = "";
            
            if (history.length === 0) {
                historyContainer.innerHTML = '<div class="text-muted small text-center mt-3">No history yet</div>';
                return;
            }

            history.forEach(item => {
                const div = document.createElement("div");
                div.className = "history-item";
                const date = new Date(item.created_at).toLocaleString();
                div.innerHTML = `
                    <div class="history-question" title="${item.question}">${item.question}</div>
                    <div class="history-date">${date}</div>
                `;
                div.addEventListener("click", () => {
                    // Re-populate chat for this history item
                    chatWindow.innerHTML = "";
                    emptyChatMsg.style.display = "none";
                    appendMessage("user", item.question);
                    
                    let sourcesHtml = "";
                    if (item.sources) {
                        try {
                            const sources = JSON.parse(item.sources);
                            sourcesHtml = createSourcesButton(sources);
                        } catch (e) {}
                    }
                    appendMessage("bot", item.answer, sourcesHtml);
                });
                historyContainer.appendChild(div);
            });
        } catch (error) {
            console.error("Failed to load history", error);
        }
    }

    // --- Upload PDF ---
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("pdf-file");
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Uploading...';
        uploadStatus.textContent = "Uploading and processing...";
        uploadStatus.className = "mt-2 small text-primary";

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                uploadStatus.textContent = `Success! Processed ${data.chunks} chunks.`;
                uploadStatus.className = "mt-2 small text-success";
                fileInput.value = "";
            } else {
                throw new Error(data.detail || "Upload failed");
            }
        } catch (error) {
            uploadStatus.textContent = error.message;
            uploadStatus.className = "mt-2 small text-danger";
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Upload & Process';
        }
    });

    // --- Chat Interface ---
    function appendMessage(sender, content, extraHtml = "", isMarkdown = true) {
        if (emptyChatMsg) emptyChatMsg.style.display = "none";

        const msgDiv = document.createElement("div");
        msgDiv.className = `message message-${sender} d-flex flex-column`;

        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content shadow-sm";
        
        if (isMarkdown && typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        msgDiv.appendChild(contentDiv);

        if (extraHtml) {
            const extraDiv = document.createElement("div");
            extraDiv.innerHTML = extraHtml;
            msgDiv.appendChild(extraDiv);
        }

        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return contentDiv;
    }

    function createSourcesButton(sources) {
        if (!sources || sources.length === 0) return "";
        const sourceData = encodeURIComponent(JSON.stringify(sources));
        return `<button class="btn btn-outline-secondary sources-btn mt-2" onclick="showSources('${sourceData}')">
            <i class="bi bi-info-circle me-1"></i>View ${sources.length} Source(s)
        </button>`;
    }

    window.showSources = function(encodedSources) {
        try {
            const sources = JSON.parse(decodeURIComponent(encodedSources));
            sourceModalBody.innerHTML = "";
            sources.forEach((s, idx) => {
                let text = s.content || "";
                if (!text && s.page_content) text = s.page_content; // fallback depending on structure
                
                const div = document.createElement("div");
                div.className = "mb-3 p-3 bg-light rounded border";
                div.innerHTML = `
                    <div class="fw-bold mb-2 text-primary">
                        Source ${idx + 1}: ${s.metadata?.filename || s.filename || 'Unknown'} (Page ${s.metadata?.page || s.page || 'N/A'})
                    </div>
                    <div class="small text-muted" style="white-space: pre-wrap;">${text}</div>
                `;
                sourceModalBody.appendChild(div);
            });
            const modal = new bootstrap.Modal(document.getElementById('sourceModal'));
            modal.show();
        } catch (e) {
            console.error("Error parsing sources", e);
        }
    };

    function appendTypingIndicator() {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message message-bot d-flex flex-column";
        msgDiv.id = "typing-indicator";
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content shadow-sm";
        contentDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        msgDiv.appendChild(contentDiv);
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return msgDiv;
    }

    queryForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage("user", query, "", false);
        queryInput.value = "";
        
        const isStreaming = streamToggle.checked;
        const typingIndicator = appendTypingIndicator();

        try {
            if (!isStreaming) {
                // Non-streaming standard fetch
                const res = await fetch("/api/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: query, stream: false })
                });
                
                typingIndicator.remove();
                
                if (!res.ok) {
                    throw new Error("Query failed");
                }
                
                const data = await res.json();
                const sourcesHtml = createSourcesButton(data.sources);
                appendMessage("bot", data.answer, sourcesHtml);
                loadHistory(); // Refresh history
            } else {
                // Streaming with Server-Sent Events / Chunked response
                const res = await fetch("/api/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: query, stream: true })
                });
                
                typingIndicator.remove();
                
                if (!res.ok) {
                    throw new Error("Stream failed");
                }
                
                // Create an empty bot message
                const contentDiv = appendMessage("bot", "");
                const reader = res.body.getReader();
                const decoder = new TextDecoder("utf-8");
                let fullText = "";
                let isSourcesSection = false;
                let sourcesText = "";
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    fullText += chunk;
                    
                    // Basic parsing logic: We prepended SOURCES: and ANSWER: in our rag.py
                    if (fullText.includes("SOURCES:\n") && fullText.includes("ANSWER:\n")) {
                        const parts = fullText.split("ANSWER:\n");
                        const answerText = parts[1] || "";
                        contentDiv.innerHTML = typeof marked !== 'undefined' ? marked.parse(answerText) : answerText;
                    } else if (fullText.includes("ANSWER:\n")) {
                        // fallback
                    } else {
                        // still reading sources or just plain text
                        contentDiv.textContent = "Processing sources and generating answer...";
                    }
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                }
                
                // Final render
                if (fullText.includes("ANSWER:\n")) {
                    const parts = fullText.split("ANSWER:\n");
                    const sourcesStr = parts[0].replace("SOURCES:\n", "").trim();
                    const answerText = parts[1] || "";
                    contentDiv.innerHTML = typeof marked !== 'undefined' ? marked.parse(answerText) : answerText;
                    
                    // We don't have full source objects in streaming right now, just strings.
                    // A simple workaround to show text sources.
                    if (sourcesStr) {
                         const extraDiv = document.createElement("div");
                         extraDiv.className = "mt-2 small text-muted";
                         extraDiv.innerHTML = "<strong>Extracted From:</strong><br>" + sourcesStr.replace(/\n/g, "<br>");
                         contentDiv.parentNode.appendChild(extraDiv);
                    }
                } else {
                    contentDiv.innerHTML = typeof marked !== 'undefined' ? marked.parse(fullText) : fullText;
                }
            }
        } catch (error) {
            typingIndicator.remove();
            appendMessage("bot", "Error: " + error.message, "", false);
        }
    });

    // --- Cleanup Buttons ---
    clearDbBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to clear the vector database? All uploaded documents will be lost.")) return;
        try {
            await fetch("/api/documents", { method: "DELETE" });
            alert("Vector database cleared.");
        } catch (e) {
            alert("Error clearing database.");
        }
    });

    clearHistoryBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to clear chat history?")) return;
        try {
            await fetch("/api/history", { method: "DELETE" });
            loadHistory();
            chatWindow.innerHTML = "";
            emptyChatMsg.style.display = "block";
            chatWindow.appendChild(emptyChatMsg);
            alert("History cleared.");
        } catch (e) {
            alert("Error clearing history.");
        }
    });

    // Init
    loadHistory();
});
