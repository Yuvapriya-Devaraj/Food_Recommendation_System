// -------------------------------
// SCROLL DOT LOGIC
// -------------------------------
const wrapper = document.getElementById("cardWrapper");
const dots = document.querySelectorAll("#dots span");

dots.forEach((dot, i) => {
  dot.addEventListener("click", () => {
    wrapper.scrollTo({
      left: wrapper.clientWidth * i,
      behavior: "smooth",
    });
  });
});

wrapper.addEventListener("scroll", () => {
  const index = Math.round(wrapper.scrollLeft / wrapper.clientWidth);

  dots.forEach((dot) => dot.classList.remove("active"));
  dots[index]?.classList.add("active");
});

// -------------------------------
// BACK BUTTON
// -------------------------------
function goBack() {
  window.history.back();
}

// -------------------------------
// FOOD SELECTION + MODAL
// -------------------------------
let selectedFood = "";

// Attach click event to cards
wrapper.addEventListener("click", (e) => {
  const card = e.target.closest(".card");

  if (!card) return;

  selectFood(card);
});

function selectFood(card) {

  selectedFood = card.dataset.food;

  document.getElementById("confirmText").innerText =
    `Are you going to eat ${selectedFood} now?`;

  document.getElementById("confirmModal").classList.remove("hidden");

}

function closeModal() {
  document.getElementById("confirmModal").classList.add("hidden");
}

// -------------------------------
// SAVE HISTORY
// -------------------------------
function saveFood() {
  const kidId = localStorage.getItem("kid_id");

  if (!kidId) {
    alert("No kid selected!");
    return;
  }

  fetch("http://127.0.0.1:5000/history", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      kid_id: kidId,
      food_name: selectedFood,
      liked: true,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "saved") {
        alert(`✅ ${selectedFood} added to history!`);
      } else {
        alert("❌ Error saving food.");
      }

      closeModal();
    })
    .catch((err) => {
      console.error("Error:", err);
      alert("Network error!");
      closeModal();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const kidId = localStorage.getItem("kid_id");
    const kidNickname = localStorage.getItem("kid_nickname");

    if (!kidId) {
        window.location.href = "/select"; // redirect if no kid
    }

    document.getElementById("kid-nickname").textContent = kidNickname || "Kid";

    // --- Dynamic Score & Reward ---
    // Example: fetch from backend API (replace URL with your endpoint)
    fetch(`/api/kids/${kidId}/score`) 
      .then(response => response.json())
      .then(data => {
          const score = data.score || 0; // total stars
          const rewardThreshold = 100; // threshold to claim reward

          // Update My Stars card
          const starsCard = document.querySelector(".bg-yellow-100 p:nth-child(3)");
          if(starsCard) starsCard.textContent = score;

          // Update Reward card
          const rewardCard = document.querySelector(".bg-pink-100 p:nth-child(3)");
          if(rewardCard) {
              if(score >= rewardThreshold) {
                  rewardCard.textContent = "Claim 🎉";
                  rewardCard.parentElement.querySelector("p:nth-child(4)").textContent = "You've earned a reward!";
              } else {
                  rewardCard.textContent = "Locked 🔒";
                  rewardCard.parentElement.querySelector("p:nth-child(4)").textContent = `Earn ${rewardThreshold - score} more stars`;
              }
          }
      })
      .catch(err => console.error("Error fetching score:", err));
});

document.addEventListener("DOMContentLoaded", function() {
    const kidId = localStorage.getItem("kid_id");
    const kidNickname = localStorage.getItem("kid_nickname");

    if (!kidId) {
        window.location.href = "/select";
    }

    document.getElementById("kid-nickname").textContent = kidNickname || "Kid";

    const rewardThreshold = 100; // stars needed for reward

    // Fetch score from backend API
    fetch(`/api/kids/${kidId}/score`)
      .then(res => res.json())
      .then(data => {
          const score = data.score || 0;

          // Update stars
          document.getElementById("my-stars").textContent = score;

          // Update rewards
          if(score >= rewardThreshold) {
              document.getElementById("my-reward").textContent = "Claim 🎉";
              document.getElementById("reward-msg").textContent = "You've earned a reward!";
          } else {
              document.getElementById("my-reward").textContent = "Locked 🔒";
              document.getElementById("reward-msg").textContent = `Earn ${rewardThreshold - score} more stars`;
          }
      })
      .catch(err => console.error("Error fetching score:", err));
});

function consumeMeal(element) {
    const kidId = localStorage.getItem("kid_id");
    if (!kidId) return;

    const foodId = element.getAttribute("data-food-id");
    const mealType = element.getAttribute("data-meal-type");

    fetch("/api/consume_food", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kid_id: kidId, food_id: foodId })
    })
    .then(res => res.json())
    .then(data => {
        // Update scoreboard
        document.getElementById("my-stars").textContent = data.total_score;

        // Reward logic
        const rewardThreshold = 100;
        const rewardEl = document.getElementById("my-reward");
        const rewardMsgEl = document.getElementById("reward-msg");

        if (data.total_score >= rewardThreshold) {
            rewardEl.textContent = "Claim 🎉";
            rewardMsgEl.textContent = "You've earned a reward!";
        } else {
            rewardEl.textContent = "Locked 🔒";
            rewardMsgEl.textContent = `Earn ${rewardThreshold - data.total_score} more stars`;
        }

        // Redirect to meal page after score update
        if (mealType === "snack") window.location.href = "/snack";
        if (mealType === "lunch") window.location.href = "/lunch";
    })
    .catch(err => console.error("Error updating score:", err));
}
