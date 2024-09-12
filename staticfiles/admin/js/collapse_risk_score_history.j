document.addEventListener('DOMContentLoaded', function() {
    var toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.innerHTML = 'Toggle Risk Score History';
    toggleButton.style.marginBottom = '10px';
    var inlines = document.querySelectorAll('.inline-group .inline-related');
    var riskScoreHistoryInline = null;

    inlines.forEach(function(inline) {
        var header = inline.querySelector('h2');
        if (header && header.textContent.trim() === 'Risk Score Historys') {
            riskScoreHistoryInline = inline;
            inline.style.display = 'none';
        }
    });

    if (riskScoreHistoryInline) {
        riskScoreHistoryInline.parentNode.insertBefore(toggleButton, riskScoreHistoryInline);
        toggleButton.addEventListener('click', function() {
            if (riskScoreHistoryInline.style.display === 'none') {
                riskScoreHistoryInline.style.display = 'block';
            } else {
                riskScoreHistoryInline.style.display = 'none';
            }
        });
    }
});
