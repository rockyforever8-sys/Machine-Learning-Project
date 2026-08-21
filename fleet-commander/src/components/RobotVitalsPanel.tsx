import { X, Battery, MapPin, Activity, ListChecks } from 'lucide-react'
import { RobotAvatar } from './RobotAvatar'
import type { Robot, Task } from '../types'

const statusLabels: Record<Robot['status'], string> = {
  idle: 'Idle',
  working: 'Working',
  charging: 'Charging',
  error: 'Error',
}

interface RobotVitalsPanelProps {
  robot: Robot
  tasks: Task[]
  onClose: () => void
}

export function RobotVitalsPanel({ robot, tasks, onClose }: RobotVitalsPanelProps) {
  const robotTasks = tasks.filter(t => robot.taskIds.includes(t.id))
  const avgProgress = robotTasks.length
    ? Math.round(robotTasks.reduce((s, t) => s + t.progress, 0) / robotTasks.length)
    : 0

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full sm:max-w-md bg-white rounded-t-2xl sm:rounded-2xl shadow-2xl p-5 animate-in slide-in-from-bottom duration-300 max-h-[85vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>

        <div className="flex items-center gap-4 mb-5">
          <RobotAvatar color={robot.color} size={56} status={robot.status} selected />
          <div>
            <h3 className="text-lg font-bold text-gray-900">{robot.name}</h3>
            <p className="text-sm text-gray-500">{statusLabels[robot.status]}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          <VitalCard
            icon={<Battery className="w-4 h-4 text-accent" />}
            label="Battery"
            value={`${robot.battery}%`}
            bar={robot.battery}
            barColor={robot.battery > 50 ? '#2563eb' : robot.battery > 20 ? '#d97706' : '#dc2626'}
          />
          <VitalCard
            icon={<Activity className="w-4 h-4 text-accent" />}
            label="Task Progress"
            value={`${avgProgress}%`}
            bar={avgProgress}
            barColor={robot.color}
          />
        </div>

        <div className="flex items-start gap-2 p-3 bg-gray-50 rounded-xl mb-4">
          <MapPin className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs text-gray-400 font-medium">Location</p>
            <p className="text-sm text-gray-700">{robot.location}</p>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <ListChecks className="w-4 h-4 text-accent" />
            <h4 className="text-sm font-semibold text-gray-800">
              Assigned Tasks ({robotTasks.length})
            </h4>
          </div>
          {robotTasks.length === 0 ? (
            <p className="text-sm text-gray-400 py-3 text-center">No tasks assigned</p>
          ) : (
            <div className="space-y-2">
              {robotTasks.map(task => (
                <div key={task.id} className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{task.title}</p>
                    <p className="text-xs text-gray-500">{task.duration}m · {task.priority}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold" style={{ color: robot.color }}>
                      {task.progress}%
                    </span>
                    <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${task.progress}%`, backgroundColor: robot.color }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function VitalCard({
  icon,
  label,
  value,
  bar,
  barColor,
}: {
  icon: React.ReactNode
  label: string
  value: string
  bar: number
  barColor: string
}) {
  return (
    <div className="p-3 bg-gray-50 rounded-xl">
      <div className="flex items-center gap-1.5 mb-1">
        {icon}
        <span className="text-xs text-gray-500 font-medium">{label}</span>
      </div>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      <div className="h-1.5 bg-gray-200 rounded-full mt-2 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${bar}%`, backgroundColor: barColor }}
        />
      </div>
    </div>
  )
}
