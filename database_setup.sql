-- StudyStride 数据库初始化脚本
-- 运行此脚本以设置完整的数据库结构

-- ============================================
-- 1. 创建 public.users 表（解决注册错误）
-- ============================================
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. 创建 study_sessions 表
-- ============================================
CREATE TABLE IF NOT EXISTS public.study_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  content TEXT,
  duration INTEGER NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE,
  session_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 为 study_sessions 表创建索引
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON public.study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_session_date ON public.study_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_study_sessions_start_time ON public.study_sessions(start_time DESC);

-- ============================================
-- 3. 创建 subjects 表
-- ============================================
CREATE TABLE IF NOT EXISTS public.subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 为 subjects 表创建索引
CREATE INDEX IF NOT EXISTS idx_subjects_user_id ON public.subjects(user_id);
CREATE INDEX IF NOT EXISTS idx_subjects_created_at ON public.subjects(created_at ASC);

-- ============================================
-- 4. 创建 user_settings 表
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_settings (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  reminder_interval INTEGER DEFAULT 30,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 5. 行级安全策略 (RLS) - 安全配置
-- ============================================

-- 启用 RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

-- public.users 表的 RLS 策略
CREATE POLICY "Users can view their own data"
  ON public.users
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own data"
  ON public.users
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- study_sessions 表的 RLS 策略
CREATE POLICY "Users can view their own study sessions"
  ON public.study_sessions
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own study sessions"
  ON public.study_sessions
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own study sessions"
  ON public.study_sessions
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own study sessions"
  ON public.study_sessions
  FOR DELETE
  USING (auth.uid() = user_id);

-- subjects 表的 RLS 策略
CREATE POLICY "Users can view their own subjects"
  ON public.subjects
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subjects"
  ON public.subjects
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own subjects"
  ON public.subjects
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own subjects"
  ON public.subjects
  FOR DELETE
  USING (auth.uid() = user_id);

-- user_settings 表的 RLS 策略
CREATE POLICY "Users can view their own settings"
  ON public.user_settings
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own settings"
  ON public.user_settings
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own settings"
  ON public.user_settings
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own settings"
  ON public.user_settings
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================
-- 6. 创建触发器函数 - 自动同步 auth.users 到 public.users
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, created_at)
  VALUES (NEW.id, NEW.email, NEW.created_at);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 7. 创建触发器 - 在 auth.users 表上触发
-- ============================================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- 8. 创建更新时间戳的触发器函数
-- ============================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 9. 为所有表添加更新时间戳触发器
-- ============================================
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_study_sessions_updated_at ON public.study_sessions;
CREATE TRIGGER update_study_sessions_updated_at
  BEFORE UPDATE ON public.study_sessions
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_subjects_updated_at ON public.subjects;
CREATE TRIGGER update_subjects_updated_at
  BEFORE UPDATE ON public.subjects
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_settings_updated_at ON public.user_settings;
CREATE TRIGGER update_user_settings_updated_at
  BEFORE UPDATE ON public.user_settings
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================
-- 完成！
-- ============================================
