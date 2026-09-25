import { useCallback, useRef, useState } from 'react';
import { ApiError } from '@/services/httpClient';

/**
 * Holds form state and maps field errors returned by the API back onto the
 * inputs that produced them.
 */
export function useForm(initialValues, onSubmit, { resetOnSuccess = false } = {}) {
  // Kept in a ref so reset does not depend on a literal recreated each render.
  const initialRef = useRef(initialValues);

  const [values, setValues] = useState(initialValues);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((event) => {
    const { name, value, type, checked } = event.target;
    setValues((current) => ({ ...current, [name]: type === 'checkbox' ? checked : value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
  }, []);

  const reset = useCallback(() => {
    setValues(initialRef.current);
    setFieldErrors({});
    setFormError(null);
  }, []);

  const handleSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      setIsSubmitting(true);
      setFormError(null);
      setFieldErrors({});

      try {
        await onSubmit(values);
        // Password forms must not keep the old secret on screen after a
        // successful change.
        if (resetOnSuccess) reset();
      } catch (error) {
        if (error instanceof ApiError && Object.keys(error.details).length > 0) {
          setFieldErrors(error.details);
        }
        setFormError(error.message);
      } finally {
        setIsSubmitting(false);
      }
    },
    [onSubmit, values, resetOnSuccess, reset],
  );

  return { values, fieldErrors, formError, isSubmitting, handleChange, handleSubmit, reset };
}
