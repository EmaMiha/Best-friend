document.addEventListener("DOMContentLoaded", function () {
    const openGameModalBtn = document.getElementById("openGameModal");
    const gameModal = new bootstrap.Modal(document.getElementById("gameModal"));

    openGameModalBtn.addEventListener("click", function () {
        gameModal.show();
    });

    document.getElementById("checkGuess").addEventListener("click", function () {
        const guess = parseInt(document.getElementById("guessNumber").value);
        const winningNumber = Math.floor(Math.random() * 5) + 1;
        const message = document.getElementById("gameMessage");

        if (guess === winningNumber) {
            const discountCode = `SAVE${Math.random() > 0.5 ? '10' : '20'}`;
            message.innerHTML = `🎉 You won! Use discount code: <strong>${discountCode}</strong>`;
            message.classList.add("text-success");
        } else {
            message.innerHTML = "❌ Sorry, try again!";
            message.classList.add("text-danger");
        }
    });
<<<<<<< HEAD
});




=======
});
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
