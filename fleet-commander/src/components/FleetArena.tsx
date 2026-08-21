import { RobotAvatar } from './RobotAvatar'
import type { Robot } from '../types'

interface FleetArenaProps {
  robots: Robot[]
  selectedRobotId: string | null
  onSelectRobot: (id: string) => void
}

export function FleetArena({ robots, selectedRobotId, onSelectRobot }: FleetArenaProps) {
  return (
    <div className="relative w-full aspect-[16/9] sm:aspect-[2/1] bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl border border-gray-200 overflow-hidden">
      <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#d1d5db" strokeWidth="0.5" opacity="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        <ellipse cx="50%" cy="50%" rx="35%" ry="30%" fill="none" stroke="#2563eb" strokeWidth="1" strokeDasharray="6 4" opacity="0.2" />
        <ellipse cx="50%" cy="50%" rx="20%" ry="18%" fill="none" stroke="#2563eb" strokeWidth="0.5" strokeDasharray="4 3" opacity="0.15" />

        <text x="3%" y="5%" className="fill-gray-400 text-[10px] sm:text-xs" style={{ fontSize: 'clamp(8px, 2vw, 12px)' }}>
          FLEET ARENA — LIVE
        </text>
      </svg>

      {robots.map(robot => {
        const isSelected = robot.id === selectedRobotId
        return (
          <button
            key={robot.id}
            onClick={() => onSelectRobot(robot.id)}
            className={`
              absolute transform -translate-x-1/2 -translate-y-1/2
              flex flex-col items-center transition-all duration-300
              ${isSelected ? 'z-10 scale-110' : 'z-0 hover:scale-105'}
            `}
            style={{ left: `${robot.arenaX}%`, top: `${robot.arenaY}%` }}
          >
            <div className={`
              p-1.5 rounded-xl bg-white/90 backdrop-blur-sm shadow-md
              ${isSelected ? 'ring-2 ring-accent shadow-lg' : 'border border-gray-200'}
            `}>
              <RobotAvatar color={robot.color} size={36} status={robot.status} selected={isSelected} />
            </div>
            <span className={`
              mt-1 text-[9px] sm:text-[10px] font-semibold px-1.5 py-0.5 rounded-full
              ${isSelected ? 'bg-accent text-white' : 'bg-white/80 text-gray-600'}
            `}>
              {robot.name}
            </span>
            <div className="flex items-center gap-0.5 mt-0.5">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  backgroundColor: robot.battery > 50 ? '#22c55e' : robot.battery > 20 ? '#f59e0b' : '#ef4444',
                }}
              />
              <span className="text-[8px] sm:text-[9px] text-gray-500">{robot.battery}%</span>
            </div>
          </button>
        )
      })}
    </div>
  )
}
