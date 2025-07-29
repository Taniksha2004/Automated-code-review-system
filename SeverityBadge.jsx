const SeverityBadge = ({ severity, className = "" }) => {
  const getSeverityClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "severity-critical"
      case "error":
        return "severity-error"
      case "warning":
        return "severity-warning"
      case "info":
        return "severity-info"
      default:
        return "severity-info"
    }
  }

  return <span className={`${getSeverityClass(severity)} ${className}`}>{severity}</span>
}

export default SeverityBadge
