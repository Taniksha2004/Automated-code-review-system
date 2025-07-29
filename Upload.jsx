"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { reviewsAPI } from "../services/api"
import LoadingSpinner from "../components/Common/LoadingSpinner"
import { CloudArrowUpIcon, DocumentTextIcon } from "@heroicons/react/24/outline"

const Upload = () => {
  const [formData, setFormData] = useState({
    filename: "",
    language: "",
    code_content: "",
  })
  const [dragActive, setDragActive] = useState(false)

  const queryClient = useQueryClient()

  // Get supported languages
  const { data: languages, isLoading: languagesLoading } = useQuery({
    queryKey: ["languages"],
    queryFn: reviewsAPI.getLanguages,
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: reviewsAPI.createSubmission,
    onSuccess: () => {
      queryClient.invalidateQueries(["submissions"])
      setFormData({ filename: "", language: "", code_content: "" })
      alert("Code submitted successfully for review!")
    },
    onError: (error) => {
      alert("Failed to submit code: " + (error.response?.data?.detail || error.message))
    },
  })

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.filename || !formData.language || !formData.code_content) {
      alert("Please fill in all fields")
      return
    }
    submitMutation.mutate(formData)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      const reader = new FileReader()

      reader.onload = (event) => {
        const extension = file.name.split(".").pop().toLowerCase()
        const languageMap = {
          py: "python",
          js: "javascript",
          ts: "typescript",
          jsx: "javascript",
          tsx: "typescript",
        }

        setFormData({
          filename: file.name,
          language: languageMap[extension] || "",
          code_content: event.target.result,
        })
      }

      reader.readAsText(file)
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      const reader = new FileReader()

      reader.onload = (event) => {
        const extension = file.name.split(".").pop().toLowerCase()
        const languageMap = {
          py: "python",
          js: "javascript",
          ts: "typescript",
          jsx: "javascript",
          tsx: "typescript",
        }

        setFormData({
          filename: file.name,
          language: languageMap[extension] || "",
          code_content: event.target.result,
        })
      }

      reader.readAsText(file)
    }
  }

  if (languagesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Code</h1>
        <p className="mt-1 text-sm text-gray-500">Submit your code for automated quality analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Form */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="filename" className="block text-sm font-medium text-gray-700">
                Filename
              </label>
              <input
                type="text"
                id="filename"
                name="filename"
                required
                className="input-field mt-1"
                placeholder="e.g., main.py"
                value={formData.filename}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="language" className="block text-sm font-medium text-gray-700">
                Language
              </label>
              <select
                id="language"
                name="language"
                required
                className="input-field mt-1"
                value={formData.language}
                onChange={handleChange}
              >
                <option value="">Select a language</option>
                {languages?.data?.map((lang) => (
                  <option key={lang.id} value={lang.id}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="code_content" className="block text-sm font-medium text-gray-700">
                Code Content
              </label>
              <textarea
                id="code_content"
                name="code_content"
                required
                rows={12}
                className="input-field mt-1 font-mono text-sm"
                placeholder="Paste your code here..."
                value={formData.code_content}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              disabled={submitMutation.isPending}
              className="w-full btn-primary flex items-center justify-center"
            >
              {submitMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <CloudArrowUpIcon className="w-5 h-5 mr-2" />
                  Submit for Review
                </>
              )}
            </button>
          </form>
        </div>

        {/* File Drop Zone */}
        <div className="card">
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="mt-2 block text-sm font-medium text-gray-900">Drop files here or click to upload</span>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="sr-only"
                  accept=".py,.js,.ts,.jsx,.tsx"
                  onChange={handleFileInput}
                />
              </label>
              <p className="mt-2 text-xs text-gray-500">Supports: Python, JavaScript, TypeScript files</p>
            </div>
          </div>

          {/* Upload Tips */}
          <div className="mt-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Upload Tips</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Maximum file size: 1MB</li>
              <li>• Supported languages: Python, JavaScript, TypeScript</li>
              <li>• Analysis typically takes 30-60 seconds</li>
              <li>• You'll receive detailed feedback on code quality</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload
