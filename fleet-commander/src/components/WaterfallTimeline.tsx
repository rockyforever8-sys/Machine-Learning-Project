import { useDroppable } from '@dnd-kit/core'
import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical } from 'lucide-react'
import type { Robot, Task } from '../types'

const priorityBarColors: Record<Task['priority'], string> = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#22c55e',
}

interface WaterfallTimelineProps {
  robots: Robot[]
  tasks: Task[]
}

export function WaterfallTimeline({ robots, tasks }: WaterfallTimelineProps) {
  const maxDuration = 120

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-800">Task Waterfall</h2>
        <span className="text-xs text-gray-400">Drag tasks between robots</span>
      </div>

      <div className="overflow-x-auto -mx-1 px-1">
        <div className="min-w-[500px]">
          <div className="flex border-b border-gray-100 pb-2 mb-1">
            <div className="w-24 sm:w-28 shrink-0" />
            <div className="flex-1 flex justify-between text-[10px] text-gray-400 px-1">
              {[0, 30, 60, 90, 120].map(m => (
                <span key={m}>{m}m</span>
              ))}
            </div>
          </div>

          <div className="space-y-1">
            {robots.map(robot => (
              <WaterfallRow
                key={robot.id}
                robot={robot}
                tasks={tasks.filter(t => robot.taskIds.includes(t.id))}
                maxDuration={maxDuration}
                color={robot.color}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function WaterfallRow({
  robot,
  tasks,
  maxDuration,
  color,
}: {
  robot: Robot
  tasks: Task[]
  maxDuration: number
  color: string
}) {
  const { setNodeRef, isOver } = useDroppable({
    id: `waterfall-${robot.id}`,
    data: { type: 'robot', robotId: robot.id },
  })

  return (
    <div
      ref={setNodeRef}
      className={`
        flex items-center rounded-lg transition-colors
        ${isOver ? 'bg-blue-50 ring-1 ring-accent/30' : 'hover:bg-gray-50'}
      `}
    >
      <div className="w-24 sm:w-28 shrink-0 pr-2">
        <p className="text-xs font-semibold text-gray-700 truncate">{robot.name}</p>
        <p className="text-[10px] text-gray-400">{tasks.length} tasks</p>
      </div>

      <div className="flex-1 relative h-10 bg-gray-50 rounded-lg border border-gray-100 overflow-hidden">
        {[30, 60, 90].map(m => (
          <div
            key={m}
            className="absolute top-0 bottom-0 border-l border-gray-200/60"
            style={{ left: `${(m / maxDuration) * 100}%` }}
          />
        ))}

        {tasks.map(task => (
          <WaterfallTaskBar key={task.id} task={task} maxDuration={maxDuration} robotColor={color} />
        ))}

        {tasks.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-[10px] text-gray-300">
            Drop tasks here
          </div>
        )}
      </div>
    </div>
  )
}

function WaterfallTaskBar({
  task,
  maxDuration,
  robotColor,
}: {
  task: Task
  maxDuration: number
  robotColor: string
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `waterfall-task-${task.id}`,
    data: { type: 'task', task },
  })

  const left = (task.startOffset / maxDuration) * 100
  const width = Math.max((task.duration / maxDuration) * 100, 8)

  const style = {
    left: `${left}%`,
    width: `${width}%`,
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 50 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="absolute top-1 bottom-1 rounded-md cursor-grab active:cursor-grabbing touch-none group"
      {...listeners}
      {...attributes}
    >
      <div
        className="h-full rounded-md flex items-center px-1.5 gap-0.5 overflow-hidden shadow-sm"
        style={{
          backgroundColor: priorityBarColors[task.priority],
          opacity: 0.85,
        }}
      >
        <GripVertical className="w-2.5 h-2.5 text-white/60 shrink-0" />
        <span className="text-[9px] sm:text-[10px] text-white font-medium truncate">
          {task.title}
        </span>
      </div>

      {task.progress > 0 && (
        <div
          className="absolute bottom-0 left-0 h-0.5 rounded-b-md"
          style={{ width: `${task.progress}%`, backgroundColor: robotColor }}
        />
      )}
    </div>
  )
}
