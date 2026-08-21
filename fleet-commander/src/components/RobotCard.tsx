import { useDroppable } from '@dnd-kit/core'
import { Battery, MapPin } from 'lucide-react'
import { RadialProgress } from './RadialProgress'
import { RobotAvatar } from './RobotAvatar'
import type { Robot, Task } from '../types'

const statusLabels: Record<Robot['status'], string> = {
  idle: 'Idle',
  working: 'Working',
  charging: 'Charging',
  error: 'Error',
}

const statusColors: Record<Robot['status'], string> = {
  idle: 'bg-gray-100 text-gray-600',
  working: 'bg-blue-100 text-blue-700',
  charging: 'bg-amber-100 text-amber-700',
  error: 'bg-red-100 text-red-700',
}

interface RobotCardProps {
  robot: Robot
  tasks: Task[]
  selected: boolean
  onSelect: () => void
}

export function RobotCard({ robot, tasks, selected, onSelect }: RobotCardProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: `robot-${robot.id}`,
    data: { type: 'robot', robotId: robot.id },
  })

  const robotTasks = tasks.filter(t => robot.taskIds.includes(t.id))
  const avgProgress = robotTasks.length
    ? Math.round(robotTasks.reduce((s, t) => s + t.progress, 0) / robotTasks.length)
    : 0

  return (
    <div
      ref={setNodeRef}
      onClick={onSelect}
      className={`
        relative flex flex-col items-center p-3 rounded-2xl bg-white border-2
        transition-all cursor-pointer select-none
        ${selected ? 'border-accent shadow-lg shadow-accent/10' : 'border-gray-200 hover:border-gray-300'}
        ${isOver ? 'border-accent bg-blue-50 scale-[1.02] shadow-lg shadow-accent/20' : ''}
      `}
    >
      {isOver && (
        <div className="absolute inset-0 rounded-2xl border-2 border-dashed border-accent animate-pulse pointer-events-none" />
      )}

      <RadialProgress value={robot.battery} size={72} color={robot.color}>
        <RobotAvatar color={robot.color} size={40} status={robot.status} selected={selected} />
      </RadialProgress>

      <p className="mt-2 text-sm font-semibold text-gray-800 truncate w-full text-center">
        {robot.name}
      </p>

      <div className="flex items-center gap-1 mt-1">
        <Battery className="w-3 h-3 text-gray-400" />
        <span className="text-xs text-gray-500">{robot.battery}%</span>
      </div>

      <span className={`mt-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium ${statusColors[robot.status]}`}>
        {statusLabels[robot.status]}
      </span>

      {robotTasks.length > 0 && (
        <div className="mt-2 w-full">
          <div className="flex justify-between text-[10px] text-gray-400 mb-0.5">
            <span>{robotTasks.length} task{robotTasks.length > 1 ? 's' : ''}</span>
            <span>{avgProgress}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${avgProgress}%`, backgroundColor: robot.color }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center gap-1 mt-1.5 text-[10px] text-gray-400 truncate w-full justify-center">
        <MapPin className="w-2.5 h-2.5 shrink-0" />
        <span className="truncate">{robot.location}</span>
      </div>
    </div>
  )
}
