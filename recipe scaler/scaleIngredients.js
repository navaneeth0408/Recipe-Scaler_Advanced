function scaleIngredients(ingredientsList, scaleFactor) {
    // If a single string is passed, wrap it in an array for processing
    const isArray = Array.isArray(ingredientsList);
    const input = isArray ? ingredientsList : [ingredientsList];

    const scaled = input.map(ingredient => {
        // 1. Parse quantity using regex
        // Matches integer, decimal, simple fraction (1/2), or mixed fraction (1 1/2)
        const regex = /^((?:\d+\s+)?\d+\/\d+|\d+(?:\.\d+)?)\s*(.*)$/;
        const match = ingredient.trim().match(regex);

        if (match) {
            const qtyStr = match[1].trim();
            const rest = match[2].trim(); // the unit and ingredient name

            // 2. Convert fractions to decimals
            let numericQty = 0;
            if (qtyStr.includes(' ') && qtyStr.includes('/')) {
                // Mixed fraction like "1 1/2"
                const parts = qtyStr.split(' ');
                const whole = parseFloat(parts[0]);
                const fracParts = parts[1].split('/');
                numericQty = whole + (parseFloat(fracParts[0]) / parseFloat(fracParts[1]));
            } else if (qtyStr.includes('/')) {
                // Simple fraction like "1/2"
                const fracParts = qtyStr.split('/');
                numericQty = parseFloat(fracParts[0]) / parseFloat(fracParts[1]);
            } else {
                // Integer or decimal like "2" or "1.5"
                numericQty = parseFloat(qtyStr);
            }

            // 3. Multiply by scale factor
            const scaledQty = numericQty * scaleFactor;

            // 4. Convert back to readable number
            // Keep integers as integers, hide trailing zeros for decimals
            const formattedQty = scaledQty % 1 === 0
                ? scaledQty.toString()
                : scaledQty.toFixed(2).replace(/\.?0+$/, '');

            // 5. Rebuild ingredient string
            // Do NOT prepend the scale factor, Do NOT duplicate numbers
            // Ensure UI renders: `${scaledQuantity} ${unit} ${ingredient}`
            return `${formattedQty} ${rest}`;
        }

        // If no numeric quantity was found, just return original string
        return ingredient;
    });

    return isArray ? scaled : scaled[0];
}

// Export for environment compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = scaleIngredients;
} else if (typeof window !== 'undefined') {
    window.scaleIngredients = scaleIngredients;
}
