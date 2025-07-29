"use client"

import { createContext, useContext, useState, useEffect } from "react"
import { authAPI } from "../services/api"

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem("access_token")
      if (token) {
        const response = await authAPI.getProfile()
        setUser(response.data)
        setIsAuthenticated(true)
      }
    } catch (error) {
      console.error("Auth check failed:", error)
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      const { user, tokens } = response.data

      localStorage.setItem("access_token", tokens.access)
      localStorage.setItem("refresh_token", tokens.refresh)

      setUser(user)
      setIsAuthenticated(true)

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      }
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      const { user, tokens } = response.data

      localStorage.setItem("access_token", tokens.access)
      localStorage.setItem("refresh_token", tokens.refresh)

      setUser(user)
      setIsAuthenticated(true)

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || "Registration failed",
      }
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token")
      if (refreshToken) {
        await authAPI.logout(refreshToken)
      }
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
