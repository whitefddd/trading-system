<template>
  <div class="login-form">
    <h3>登录</h3>
    <form @submit.prevent="login">
      <div class="form-group">
        <label>用户名</label>
        <input v-model="credentials.username" type="text" required>
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="credentials.password" type="password" required>
      </div>
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    async login() {
      try {
        const formData = new FormData()
        formData.append('username', this.credentials.username)
        formData.append('password', this.credentials.password)
        
        const response = await fetch('http://localhost:8000/api/token', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          const data = await response.json()
          localStorage.setItem('token', data.access_token)
          this.$emit('login-success')
        } else {
          console.error('Login failed')
        }
      } catch (error) {
        console.error('Error during login:', error)
      }
    }
  }
}
</script> 