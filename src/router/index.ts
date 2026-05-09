import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/History.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/Settings.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/community',
      name: 'community',
      component: () => import('../views/Community.vue')
    },
    {
      path: '/community/post/:id',
      name: 'post-detail',
      component: () => import('../views/PostDetail.vue')
    },
    {
      path: '/community/post/create',
      name: 'create-post',
      component: () => import('../views/CreatePost.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileSettings.vue')
    }
  ]
})

export default router
