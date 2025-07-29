import { useQuery } from "@tanstack/react-query"
import { dashboardAPI } from "../services/api"
import LoadingSpinner from "../components/Common/LoadingSpinner"
import StatusBadge from "../components/Common/StatusBadge"
import { DocumentTextIcon, ExclamationTriangleIcon, CheckCircleIcon, ClockIcon } from "@heroicons/react/24/outline"

const Dashboard = () => {
  const { data: overview, isLoading } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: dashboardAPI.getOverview,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const stats = overview?.data || {}

  const statCards = [
    {
      name: "Total Submissions",
      value: stats.total_submissions || 0,
      icon: DocumentTextIcon,
      color: "blue",
    },
    {
      name: "Completed",
      value: stats.completed_submissions || 0,
      icon: CheckCircleIcon,
      color: "green",
    },
    {
      name: "Pending",
      value: stats.pending_submissions || 0,
      icon: ClockIcon,
      color: "yellow",
    },
    {
      name: "Total Issues",
      value: stats.total_issues || 0,
      icon: ExclamationTriangleIcon,
      color: "red",
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Overview of your code review activities</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className={`h-8 w-8 text-${stat.color}-600`} aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                  <dd className="text-lg font-medium text-gray-900">{stat.value.toLocaleString()}</dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Average Score */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Average Score</h3>
            <p className="text-sm text-gray-500">Overall code quality score across all submissions</p>
          </div>
          <div className="text-3xl font-bold text-blue-600">{stats.average_score || 0}%</div>
        </div>
        <div className="mt-4">
          <div className="bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${stats.average_score || 0}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Recent Submissions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Submissions</h3>
          <a href="/submissions" className="text-sm text-blue-600 hover:text-blue-500">
            View all
          </a>
        </div>

        {stats.recent_submissions?.length > 0 ? (
          <div className="space-y-3">
            {stats.recent_submissions.map((submission) => (
              <div key={submission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{submission.filename}</p>
                    <p className="text-xs text-gray-500">
                      {submission.language_name} • {new Date(submission.submitted_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {submission.result && (
                    <span className="text-sm font-medium text-gray-900">{submission.result.overall_score}%</span>
                  )}
                  <StatusBadge status={submission.status} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No submissions yet</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by uploading your first code file.</p>
            <div className="mt-6">
              <a href="/upload" className="btn-primary">
                Upload Code
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
