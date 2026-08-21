import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Clock } from 'lucide-react'
import type { Task } from '../types'

const priorityColors: Record<Task['priority'], string> = {
  high: 'border-l-red-500 bg-red-50',
  medium: 'border-l-amber-500 bg-amber-50',
  low: 'border-l-green-500 bg-green-50',
}

interface TaskCardProps {
  task: Task
  compact?: boolean
}

export function TaskCard({ task, compact = false }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: task.id,
    data: { type: 'task', task },
  })

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 50 : undefined,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`
        border-l-4 rounded-lg bg-white border border-gray-200 shadow-sm
        ${priorityColors[task.priority]}
        ${compact ? 'px-2 py-1.5' : 'px-3 py-2.5'}
        ${isDragging ? 'shadow-lg ring-2 ring-accent/30' : 'hover:shadow-md'}
        transition-shadow cursor-grab active:cursor-grabbing touch-none
      `}
      {...listeners}
      {...attributes}
    >
      <div className="flex items-start gap-2">
        <GripVertical className="w-4 h-4 text-gray-300 mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className={`font-medium text-gray-800 truncate ${compact ? 'text-xs' : 'text-sm'}`}>
            {task.title}
          </p>
          <div className={`flex items-center gap-2 text-gray-500 ${compact ? 'text-[10px]' : 'text-xs'} mt-0.5`}>
            <Clock className="w-3 h-3" />
            <span>{task.duration}m</span>
            {task.progress > 0 && (
              <span className="text-accent font-medium">{task.progress}%</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
