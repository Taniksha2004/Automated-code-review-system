"use client"
import { NavLink, useLocation } from "react-router-dom"
import {
  HomeIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
  UserIcon,
  CloudArrowUpIcon,
} from "@heroicons/react/24/outline"

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon },
  { name: "Submissions", href: "/submissions", icon: DocumentTextIcon },
  { name: "Upload Code", href: "/upload", icon: CloudArrowUpIcon },
  { name: "Analytics", href: "/analytics", icon: ChartBarIcon },
  { name: "Profile", href: "/profile", icon: UserIcon },
  { name: "Settings", href: "/settings", icon: CogIcon },
]

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation()

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && <div className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden" onClick={onClose} />}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 bg-blue-600">
            <h1 className="text-xl font-bold text-white">Code Review</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`sidebar-link ${isActive ? "active" : ""}`}
                  onClick={() => window.innerWidth < 1024 && onClose()}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 text-center">Version 1.0.0</div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Sidebar
