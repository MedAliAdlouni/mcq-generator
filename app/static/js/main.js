// app/static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("✨ QuizAI frontend ready!");

  // --- Toast notification function ---
  function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    const bgColor = type === "success" 
      ? "bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 border-green-500"
      : "bg-gradient-to-r from-red-50 to-rose-50 text-red-800 border-red-500";
    
    toast.className = `${bgColor} border-l-4 rounded-lg shadow-lg px-6 py-4 min-w-[300px] max-w-md animate-slide-in-right flex items-center gap-3`;
    toast.innerHTML = `
      <span class="text-2xl">${type === "success" ? "✅" : "❌"}</span>
      <span class="flex-1 font-medium">${message}</span>
      <button onclick="this.parentElement.remove()" class="text-gray-400 hover:text-gray-600 transition">✕</button>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
      toast.style.animation = "slide-out-right 0.3s ease forwards";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // --- Upload ---
  const uploadForm = document.getElementById("uploadForm");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(uploadForm);
      const status = document.getElementById("uploadStatus");
      status.textContent = "📤 Uploading...";

      try {
        const res = await fetch("/api/documents/upload", { method: "POST", body: formData });
        const data = await res.json();

        if (res.ok) {
          status.textContent = "✅ Document uploaded successfully!";
          setTimeout(() => (window.location.href = "/documents"), 1000);
        } else {
          status.textContent = "❌ " + (data.error || "Upload error.");
        }
      } catch (err) {
        status.textContent = "⚠️ Network error.";
      }
    });
  }

  // --- Delete document ---
  const deleteButtons = document.querySelectorAll("[data-delete]");
  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.delete;
      if (!confirm("Delete this document?")) return;

      try {
        const res = await fetch(`/api/documents/${id}`, { method: "DELETE" });
        const data = await res.json();

        if (res.ok) {
          btn.closest("div.bg-white, div.bg-white\\/50, div.bg-white\\/40")?.remove();
          alert("🗑️ Document deleted!");
        } else {
          alert("❌ Error: " + (data.error || "Unable to delete."));
        }
      } catch (err) {
        alert("⚠️ Network or server error.");
      }
    });
  });

  // --- Quiz generation ---
  const genButtons = document.querySelectorAll("[data-generate]");
  genButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const docId = btn.dataset.generate;
      btn.disabled = true;
      const oldText = btn.textContent;
      btn.textContent = "⏳ Generating...";

      try {
        const res = await fetch(`/api/quizzes/generate?document_id=${docId}`, { method: "POST" });
        const data = await res.json();

        if (res.ok) {
          showToast(data.message || "Quiz generated successfully!", "success");
          
          // Update the DOM: swap buttons without page refresh
          const playDisabledBtn = document.querySelector(`[data-play-disabled="${docId}"]`);
          const generateBtn = document.querySelector(`[data-generate-btn="${docId}"]`);
          
          if (playDisabledBtn && generateBtn) {
            // Create new Play link
            const playLink = document.createElement("a");
            playLink.href = `/quizzes/play/${docId}`;
            playLink.className = "btn btn-green hover:brightness-105";
            playLink.textContent = "Play";
            
            // Create new Generated button
            const generatedBtn = document.createElement("button");
            generatedBtn.disabled = true;
            generatedBtn.className = "btn btn-yellow opacity-60 cursor-not-allowed";
            generatedBtn.title = "Quiz already generated";
            generatedBtn.textContent = "Generated";
            
            // Replace buttons
            playDisabledBtn.replaceWith(playLink);
            generateBtn.replaceWith(generatedBtn);
          }
        } else {
          showToast(data.error || "Error during generation.", "error");
          btn.textContent = oldText;
          btn.disabled = false;
        }
      } catch (err) {
        showToast("Server connection error.", "error");
        btn.textContent = oldText;
        btn.disabled = false;
      }
    });
  });

  // --- Strict Quiz Mode: one question at a time ---
  const quizContainer = document.getElementById("quizContainer");
  if (quizContainer) {
    const questions = JSON.parse(quizContainer.dataset.questions);
    const questionBox = document.getElementById("questionBox");
    const nextBtn = document.getElementById("nextBtn");
    const resultBox = document.getElementById("result");
    const progressText = document.getElementById("progress");
    const scoreDisplay = document.getElementById("scoreDisplay");

    let current = 0;
    let score = 0;
    let answered = false;

    function renderQuestion() {
      const q = questions[current];
      answered = false;
      nextBtn.classList.add("hidden");
      progressText.textContent = `Question ${current + 1} / ${questions.length}`;

      questionBox.innerHTML = `
        <p class="font-semibold mb-4">${q.question}</p>
        ${
          q.type === "qcm" && q.choices
            ? q.choices
                .map(
                  (choice) => `
            <button class="choice-btn w-full border border-gray-300 rounded-lg py-2 my-1 hover:bg-gray-50 transition">
              ${choice}
            </button>`
                )
                .join("")
            : `<textarea id="openAnswer" rows="2" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-primary" placeholder="Your answer..."></textarea>
              <button id="submitOpen" class="mt-3 bg-primary text-white px-4 py-2 rounded-lg shadow hover:bg-blue-600">Submit</button>`
        }
      `;

      if (q.type === "open") {
        document.getElementById("submitOpen").addEventListener("click", () => {
          const answer = document.getElementById("openAnswer").value.trim();
          handleAnswer(answer);
        });
      } else {
        document.querySelectorAll(".choice-btn").forEach((btn) => {
          btn.addEventListener("click", () => handleAnswer(btn.textContent.trim(), btn));
        });
      }
    }

    function handleAnswer(answer, btn = null) {
      if (answered) return;
      answered = true;
      const q = questions[current];
      const correct = q.answer?.trim().toLowerCase();

      q.user_answer = answer;
      q.is_correct = answer.toLowerCase() === correct;

      if (q.is_correct) {
        score++;
        scoreDisplay.textContent = `Score: ${score}`;
        if (btn) btn.classList.add("bg-green-100", "border-green-500");
        showFeedback("✅ Correct answer!");
      } else {
        if (btn) btn.classList.add("bg-red-100", "border-red-500");
        showFeedback(`❌ Wrong answer. Correct answer: <strong>${q.answer}</strong>`);
      }

      nextBtn.classList.remove("hidden");
    }

    function showFeedback(msg) {
      const fb = document.createElement("p");
      fb.innerHTML = msg;
      fb.className = "mt-4 text-sm text-gray-700";
      questionBox.appendChild(fb);
    }

    function handleNext() {
      current++;
      if (current < questions.length) renderQuestion();
      else showResult();
    }

    async function showResult() {
      questionBox.innerHTML = "";
      nextBtn.classList.add("hidden");
      resultBox.classList.remove("hidden");
      resultBox.innerHTML = `
        <h2 class="text-2xl font-bold mb-2">Quiz Completed</h2>
        <p class="text-lg">Final score: <strong>${score}/${questions.length}</strong></p>
      `;

      const answersData = questions.map((q) => ({
        question_id: q.id,
        user_answer: q.user_answer || "",
        is_correct: q.is_correct || false,
      }));

      try {
        const res = await fetch("/api/results/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            document_id: quizContainer.dataset.documentId || null,
            score: score,
            answers: answersData,
          }),
        });
        const data = await res.json();
        console.log("💾 Saved:", data);
      } catch (err) {
        console.error("❌ Error saving results:", err);
      }
    }

    nextBtn.addEventListener("click", handleNext);
    renderQuestion();
  }

  // --- Results visualization (/results page) ---
  const docSelect = document.getElementById("documentSelect");
  const ctx = document.getElementById("resultsChart");
  const noDataMsg = document.getElementById("noDataMessage");

  if (docSelect && ctx) {
    let chart;

    async function fetchResults(documentId) {
      const res = await fetch(`/api/results/data?document_id=${documentId}`);
      return await res.json();
    }

    async function updateChart(documentId) {
      const data = await fetchResults(documentId);

      if (!data || data.length === 0) {
        if (chart) chart.destroy();
        noDataMsg.classList.remove("hidden");
        return;
      }

      noDataMsg.classList.add("hidden");

      const labels = data.map((d) => d.played_at);
      const scores = data.map((d) => d.score);

      if (chart) chart.destroy();

      // Pastel gradient for the line
      const ctx2d = ctx.getContext("2d");
      const gradient = ctx2d.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, "rgba(37,99,235,0.4)");
      gradient.addColorStop(1, "rgba(147,197,253,0.05)");

      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Score",
              data: data.map(d => d.score),
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.15)",
              fill: true,
              tension: 0.35,
              pointRadius: 5,
              pointHoverRadius: 7,
              pointBackgroundColor: "#2563eb",
              pointBorderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 10,
              ticks: {
                stepSize: 1,
                color: "#4b5563",
                font: { family: "Inter, sans-serif", size: 12, weight: 500 },
              },
              grid: { color: "rgba(0,0,0,0.05)" },
            },
            x: {
              ticks: {
                color: "#6b7280",
                font: { family: "Inter, sans-serif", size: 12 },
              },
              grid: { display: false },
            },
          },
          plugins: {
            legend: { display: false },
            title: { display: false },
            tooltip: {
              backgroundColor: "rgba(37,99,235,0.9)",
              titleColor: "#fff",
              bodyColor: "#fff",
              cornerRadius: 6,
              padding: 10,
              displayColors: false,
            },
          },
          elements: {
            line: { borderWidth: 3 },
          },
          animation: {
            duration: 700,
            easing: "easeOutCubic",
          },
        },
      });
    }

    // Initial load
    if (docSelect.value) updateChart(docSelect.value);

    // Dynamic update
    docSelect.addEventListener("change", (e) => {
      updateChart(e.target.value);
    });
  }
});
