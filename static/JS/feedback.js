// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("feedback-form");
  const responseMessage = document.getElementById("feedback-response");

  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent form from submitting traditionally

    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    if (!email || !message) {
      responseMessage.style.color = "#d9534f"; // red
      responseMessage.textContent = "Please fill in both email and message.";
      return;
    }

    // Simulate successful submission
    responseMessage.style.color = "#0077b6"; // Signlingo blue
    responseMessage.textContent = "Thank you for your feedback! 💙 We'll get back to you if needed.";

    // Optionally reset the form
    form.reset();

    // Optional: Hide message after 5 seconds
    setTimeout(() => {
      responseMessage.textContent = "";
    }, 5000);
  });
});
