export default function AvailabilityBadge({ status }) {
  const klass =
    status === 'Available' ? 'badge badge-available' : 'badge badge-borrowed';
  return <span className={klass}>{status}</span>;
}
