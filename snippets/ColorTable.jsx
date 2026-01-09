export const ColorTable = ({ headers, colors }) => {
  // Normalize color data - handle both string and object formats
  const normalizeColorData = (data) => {
    if (typeof data === "string") {
      return { label: data.toUpperCase(), color: data };
    }
    return { ...data, label: data.label.toUpperCase() };
  };

  // Calculate relative luminance of a color using WCAG formula
  const getLuminance = (hex) => {
    // Handle rgba format
    const color = hex.startsWith("rgba") ? hex.match(/#([0-9a-f]{6})/i)?.[1] || hex : hex;

    // Remove # if present
    const cleanHex = color.replace("#", "");

    // Parse hex color
    let r = parseInt(cleanHex.substring(0, 2), 16) / 255;
    let g = parseInt(cleanHex.substring(2, 4), 16) / 255;
    let b = parseInt(cleanHex.substring(4, 6), 16) / 255;

    // Apply gamma correction
    r = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
    g = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
    b = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);

    // Calculate relative luminance using WCAG formula
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;

    return luminance;
  };

  // Determine if text should be white or black based on luminance
  const getTextColor = (bgColor) => {
    const luminance = getLuminance(bgColor);
    return luminance > 0.5 ? "text-black" : "text-white";
  };

  // Calculate grid columns based on number of headers or colors per row
  const getColumnCount = () => {
    if (colors && colors.length > 0 && colors[0].length > 0) {
      return colors[0].length;
    }
    return headers ? headers.length : 1;
  };

  const columnCount = getColumnCount();

  return (
    <div className="w-full">
      {/* Header Row - only shows if headers prop is provided */}
      {headers && headers.length > 0 && (
        <div className="grid gap-3 mb-4 pb-3 border-b" style={{ gridTemplateColumns: `repeat(${columnCount}, 1fr)` }}>
          {headers.map((header, index) => (
            <div key={index} className="text-xs font-semibold uppercase tracking-wide text-center px-2">
              {header}
            </div>
          ))}
        </div>
      )}

      {/* Color Rows */}
      <div className="flex flex-col gap-4">
        {colors &&
          colors.map((row, rowIndex) => (
            <div key={rowIndex} className="grid gap-3" style={{ gridTemplateColumns: `repeat(${columnCount}, 1fr)` }}>
              {row.map((colorItem, colIndex) => {
                const normalized = normalizeColorData(colorItem);
                const textColorClass = getTextColor(normalized.color);
                return (
                  <div key={colIndex} className="flex flex-col items-center">
                    <div
                      className={`w-full h-12 rounded flex items-center justify-center ${textColorClass}`}
                      style={{ backgroundColor: normalized.color }}
                    >
                      <div className="text-sm font-medium font-mono text-center px-2">{normalized.label}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
      </div>
    </div>
  );
};
