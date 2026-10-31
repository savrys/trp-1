
document.addEventListener("DOMContentLoaded", function () {
    const adviceButton = document.getElementById("adviceButton");
    const adviceText = document.getElementById("rideAdvice");

    const adviceList = [
        "Не забудь проверить тормоза перед поездкой!",
        "Надевай шлем для безопасности.",
        "Соблюдай правила дорожного движения.",
        "Проверь давление в шинах.",
        "Используй фонари в тёмное время суток."
    ];

    if (adviceButton && adviceText) {
        adviceButton.addEventListener("click", function () {
            const randomIndex = Math.floor(
                Math.random() * adviceList.length
            );

            adviceText.textContent = adviceList[randomIndex];
        });
    }
});
