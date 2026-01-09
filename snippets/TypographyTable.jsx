export const TypographyTable = ({ typography }) => {
  return (
    <div className="w-full space-y-8">
      {typography?.map((item, index) => (
        <div key={index}>
          {/* Title */}
          <div className="text-xs font-semibold uppercase tracking-wide mb-2">{item.name}</div>

          {/* Metadata */}
          <div className="text-xs mb-4 border-b border-gray-200 dark:border-gray-700">
            Size/Leading: {item.size}/{item.leading} • Weight: {item.weight} {item.weightNumber}
            {item.opacity && ` • ${item.opacity}% Black`}
            {item.letterSpacing && ` • Letter Spacing: ${item.letterSpacing}`}
          </div>

          {/* Preview */}
          <div
            style={{
              fontSize: `${item.size}px`,
              lineHeight: `${item.leading}px`,
              fontWeight: item.weightNumber,
              letterSpacing: item.letterSpacing ? `${item.letterSpacing}px` : "normal",
              fontFamily:
                'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
            }}
          >
            {item.preview}
          </div>
        </div>
      ))}
    </div>
  );
};
