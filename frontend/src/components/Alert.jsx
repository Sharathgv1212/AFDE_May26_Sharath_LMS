export default function Alert({ kind = 'error', message, onDismiss }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${kind}`}>
      <span>{message}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          style={{
            float: 'right',
            background: 'transparent',
            color: 'inherit',
            padding: 0,
            fontWeight: 700,
          }}
        >
          ×
        </button>
      )}
    </div>
  );
}
