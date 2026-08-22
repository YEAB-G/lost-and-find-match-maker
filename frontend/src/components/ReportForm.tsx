/**
 * ReportForm component for creating lost and found reports.
 *
 * Supports:
 * - Lost/Found toggle
 * - Required fields: title, description, location, date/time
 * - Optional fields: category, color
 * - Client-side validation
 * - Backend error display
 * - Success feedback
 */

import { useState, type FormEvent } from 'react';
import { createReport, CATEGORIES, COLORS, type ReportCreate } from '../api';
import './ReportForm.css';

interface ReportFormProps {
  onReportCreated: () => void;
}

interface FormData {
  report_type: 'lost' | 'found';
  title: string;
  description: string;
  location: string;
  reported_at: string;
  category: string;
  color: string;
}

interface FormErrors {
  title?: string;
  description?: string;
  location?: string;
  reported_at?: string;
  submit?: string;
}

const INITIAL_FORM_DATA: FormData = {
  report_type: 'lost',
  title: '',
  description: '',
  location: '',
  reported_at: '',
  category: '',
  color: '',
};

export default function ReportForm({ onReportCreated }: ReportFormProps) {
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // ============================================================================
  // Validation
  // ============================================================================

  const validate = (): FormErrors => {
    const newErrors: FormErrors = {};

    // Title validation
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.trim().length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    // Description validation
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    // Location validation
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    } else if (formData.location.trim().length > 200) {
      newErrors.location = 'Location must be 200 characters or less';
    }

    // Date validation
    if (!formData.reported_at) {
      newErrors.reported_at = 'Date and time are required';
    } else {
      const reportedDate = new Date(formData.reported_at);
      const now = new Date();
      if (reportedDate > now) {
        newErrors.reported_at = 'Date cannot be in the future';
      }
    }

    return newErrors;
  };

  // ============================================================================
  // Form Submission
  // ============================================================================

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});
    setShowSuccess(false);

    // Validate
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);

    try {
      const reportData: ReportCreate = {
        report_type: formData.report_type,
        title: formData.title.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        reported_at: new Date(formData.reported_at).toISOString(),
      };

      // Add optional fields only if provided
      if (formData.category) {
        reportData.category = formData.category;
      }
      if (formData.color) {
        reportData.color = formData.color;
      }

      await createReport(reportData);

      // Reset form
      setFormData(INITIAL_FORM_DATA);
      setShowSuccess(true);

      // Notify parent to refresh list
      onReportCreated();

      // Hide success message after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create report';
      setErrors({ submit: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="report-form-container">
      <h2>Create a Report</h2>

      {showSuccess && (
        <div className="success-message" role="status" aria-live="polite">
          ✅ Report created successfully! Check the list below.
        </div>
      )}

      {errors.submit && (
        <div className="error-message" role="alert" aria-live="assertive">
          ❌ {errors.submit}
        </div>
      )}

      <form onSubmit={handleSubmit} className="report-form">
        {/* Report Type Toggle */}
        <div className="form-group type-toggle">
          <label className="required-label">Report Type</label>
          <div className="toggle-buttons">
            <button
              type="button"
              className={`toggle-btn ${formData.report_type === 'lost' ? 'active lost' : ''}`}
              onClick={() => setFormData({ ...formData, report_type: 'lost' })}
            >
              🔴 I Lost Something
            </button>
            <button
              type="button"
              className={`toggle-btn ${formData.report_type === 'found' ? 'active found' : ''}`}
              onClick={() => setFormData({ ...formData, report_type: 'found' })}
            >
              🟢 I Found Something
            </button>
          </div>
        </div>

        {/* Title */}
        <div className="form-group">
          <label htmlFor="title" className="required-label">
            Item Title
          </label>
          <input
            id="title"
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="e.g., Black AirPods Case"
            className={errors.title ? 'error' : ''}
            maxLength={200}
            aria-required="true"
            aria-describedby={errors.title ? 'title-error' : undefined}
          />
          {errors.title && <span id="title-error" className="field-error" role="alert">{errors.title}</span>}
        </div>

        {/* Description */}
        <div className="form-group">
          <label htmlFor="description" className="required-label">
            Description
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Describe the item and where you lost/found it..."
            className={errors.description ? 'error' : ''}
            rows={3}
            aria-required="true"
            aria-describedby={errors.description ? 'description-error' : undefined}
          />
          {errors.description && <span id="description-error" className="field-error" role="alert">{errors.description}</span>}
        </div>

        {/* Location */}
        <div className="form-group">
          <label htmlFor="location" className="required-label">
            Location
          </label>
          <input
            id="location"
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            placeholder="e.g., Library, Cafeteria, Engineering Building"
            className={errors.location ? 'error' : ''}
            maxLength={200}
            aria-required="true"
            aria-describedby={errors.location ? 'location-error' : undefined}
          />
          {errors.location && <span id="location-error" className="field-error" role="alert">{errors.location}</span>}
        </div>

        {/* Date and Time */}
        <div className="form-group">
          <label htmlFor="reported_at" className="required-label">
            When did this happen?
          </label>
          <input
            id="reported_at"
            type="datetime-local"
            value={formData.reported_at}
            onChange={(e) => setFormData({ ...formData, reported_at: e.target.value })}
            className={errors.reported_at ? 'error' : ''}
            aria-required="true"
            aria-describedby={errors.reported_at ? 'reported_at-error' : undefined}
          />
          {errors.reported_at && <span id="reported_at-error" className="field-error" role="alert">{errors.reported_at}</span>}
        </div>

        {/* Optional Fields */}
        <div className="optional-section">
          <h3>Optional Details</h3>
          <p className="optional-hint">These help improve matching but are not required.</p>

          <div className="form-row">
            {/* Category */}
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                <option value="">Select category...</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Color */}
            <div className="form-group">
              <label htmlFor="color">Color</label>
              <select
                id="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              >
                <option value="">Select color...</option>
                {COLORS.map((color) => (
                  <option key={color} value={color}>
                    {color.charAt(0).toUpperCase() + color.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="submit-btn"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Report'}
        </button>
      </form>
    </div>
  );
}
