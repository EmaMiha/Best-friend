document.addEventListener("DOMContentLoaded", function () {
    let openModalBtn = document.getElementById("openGameModal");
    let checkGuessBtn = document.getElementById("checkGuess");

    if (openModalBtn) {
        openModalBtn.addEventListener("click", function () {
            let gameModal = new bootstrap.Modal(document.getElementById("gameModal"));
            gameModal.show();
        });
    }

    if (checkGuessBtn) {
        checkGuessBtn.addEventListener("click", function () {
            let userGuess = parseInt(document.getElementById("guessNumber").value);
            let randomNum = Math.floor(Math.random() * 5) + 1;
            let message = document.getElementById("gameMessage");

            if (userGuess === randomNum) {
                let discountCode = Math.floor(100000 + Math.random() * 900000);
                localStorage.setItem("discount_code", discountCode);
                message.innerHTML = `<strong>Congratulations! Your discount code is: ${discountCode}</strong>`;
            } else {
                message.innerHTML = "Sorry, you didn't win. Try again!";
            }
        });
    }
});