interface RobotAvatarProps {
  color: string
  size?: number
  status?: 'idle' | 'working' | 'charging' | 'error'
  selected?: boolean
}

export function RobotAvatar({ color, size = 48, status = 'idle', selected = false }: RobotAvatarProps) {
  const pulse = status === 'working'
  const charging = status === 'charging'

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      className={`transition-transform ${selected ? 'scale-110' : ''}`}
    >
      {pulse && (
        <circle cx="32" cy="32" r="30" fill={color} opacity="0.15">
          <animate attributeName="r" values="28;32;28" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0.05;0.2" dur="2s" repeatCount="indefinite" />
        </circle>
      )}

      <rect x="18" y="14" width="28" height="22" rx="6" fill={color} />
      <rect x="22" y="18" width="8" height="6" rx="2" fill="white" opacity="0.9" />
      <rect x="34" y="18" width="8" height="6" rx="2" fill="white" opacity="0.9" />
      <circle cx="26" cy="21" r="2" fill={color} />
      <circle cx="38" cy="21" r="2" fill={color} />

      <rect x="28" y="36" width="8" height="6" rx="2" fill={color} opacity="0.8" />
      <rect x="14" y="38" width="8" height="14" rx="3" fill={color} opacity="0.7" />
      <rect x="42" y="38" width="8" height="14" rx="3" fill={color} opacity="0.7" />
      <rect x="22" y="42" width="8" height="16" rx="3" fill={color} />
      <rect x="34" y="42" width="8" height="16" rx="3" fill={color} />

      {charging && (
        <path d="M34 8 L30 16 L34 16 L30 24" stroke="#fbbf24" strokeWidth="2" fill="none" strokeLinecap="round">
          <animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite" />
        </path>
      )}

      {status === 'error' && (
        <circle cx="50" cy="14" r="6" fill="#dc2626" />
      )}
    </svg>
  )
}
