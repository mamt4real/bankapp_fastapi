const loginForm = document.getElementById('loginform')
const registerUpdateForm = document.getElementById('register-update-form')
const passwordUpdateForm = document.getElementById('updatepassword')
const bankingForm = document.getElementById('banking')
const accountForm = document.getElementById('accountForm')

const hideAlert = () => {
  const el = document.querySelector('.alert')
  if (el) el.parentElement.removeChild(el)
}

const showAlert = (type, msg) => {
  hideAlert()
  const markup = `<div class="alert alert--${type}">${msg}</div>`
  document.querySelector('body').insertAdjacentHTML('afterbegin', markup)
  setTimeout(hideAlert, 4000)
}

const getFormData = (form) => {
  const data = {}
  for (const [key, val] of new FormData(form)) data[key] = val
  return JSON.stringify(data)
}

const handleLogin = async (e) => {
  e.preventDefault()
  const body = new URLSearchParams()
  for (const [key, val] of new FormData(e.target)) body.append(key, val)
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      credentials: 'include',
      body,
    })
    const data = await res.json()
    if (res.status == 200) {
      localStorage.setItem('token', data.access_token)
      showAlert('success', 'Login Successfully')
      setTimeout(() => (window.location = '/dashboard'), 4000)
    } else showAlert('error', data.message || data.detail)
  } catch (error) {
    console.log(error)
    showAlert('error', error.response?.data.message || error.message)
  }
}

/**
 * Handles signup or update of a customer
 */
const handleRegisterUpdate = async (e) => {
  e.preventDefault()
  const body = getFormData(e.target)
  const operation = e.target.operation?.value
  const method = operation === 'update' ? 'PUT' : 'POST'
  const url = operation === 'update' ? '/api/customers/me' : '/api/signup'
  try {
    const res = await fetch(url, {
      method,
      credentials: 'include',
      body,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
    })
    const data = await res.json()
    if (res.status >= 200 && res.status < 400) {
      if (data.access_token) localStorage.setItem('token', data.access_token)
      showAlert(
        'success',
        operation === 'update'
          ? 'Details Updated Successfully'
          : 'Registered Successfully'
      )
      setTimeout(() => setTimeout(() => (window.location = '/dashboard'), 4000))
    } else showAlert('error', data.message || data.detail)
  } catch (error) {
    console.log(error)
    showAlert('error', error.response?.data.message || error.message)
  }
}

const handlePasswordUpdate = async (e) => {
  e.preventDefault()
  const body = getFormData(e.target)
  try {
    const res = await fetch('/api/update-password', {
      method: 'PUT',
      credentials: 'include',
      body,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
    })
    const data = await res.json()
    if (res.status >= 200 && res.status < 400) {
      localStorage.setItem('token', data.access_token)
      showAlert('success', 'Password Updated Successfully')
      for (const key in JSON.parse(body))
        document.getElementById(key).value = ''
    } else {
      showAlert('error', data.message || data.detail)
    }
  } catch (error) {
    showAlert('error', error.response?.data.message || error.message)
  }
}

const handleBanking = async (e) => {
  e.preventDefault()
  const body = getFormData(e.target)
  const path = e.target.action?.value
  const accno = e.target.account_no?.value
  try {
    const res = await fetch(`/api/accounts/${accno}/${path}`, {
      method: 'POST',
      credentials: 'include',
      body,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
    })
    const data = await res.json()
    if (res.status == 200) {
      showAlert('success', data.message)
      for (const key in JSON.parse(body))
        document.getElementById(key).value = ''
      window.location = '/dashboard/accounts'
    } else {
      showAlert('error', data.message || data.detail)
    }
  } catch (error) {
    showAlert('error', error.response?.data.message || error.message)
  }
}

const handleCreateAccount = async (e) => {
  e.preventDefault()
  const body = getFormData(e.target)
  try {
    const res = await fetch(`/api/accounts`, {
      method: 'POST',
      credentials: 'include',
      body,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
    })
    const data = await res.json()
    if (res.status == 200) {
      showAlert('success', data.message)
      for (const key in JSON.parse(body))
        document.getElementById(key).value = ''
    } else {
      showAlert('error', data.message || data.detail)
    }
  } catch (error) {
    showAlert('error', error.response?.data.message || error.message)
  }
}

if (loginForm) loginForm.addEventListener('submit', handleLogin)
if (passwordUpdateForm)
  passwordUpdateForm.addEventListener('submit', handlePasswordUpdate)
if (registerUpdateForm)
  registerUpdateForm.addEventListener('submit', handleRegisterUpdate)
if (bankingForm) bankingForm.addEventListener('submit', handleBanking)
if (accountForm) accountForm.addEventListener('submit', handleCreateAccount)
