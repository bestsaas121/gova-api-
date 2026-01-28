-- Supabase SQL: Create visibility_leads table
-- Run this in the Supabase SQL Editor

CREATE TABLE visibility_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    score INTEGER NOT NULL,
    status TEXT,
    analysis_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for email lookups
CREATE INDEX idx_visibility_leads_email ON visibility_leads(email);

-- Create index for date-based queries
CREATE INDEX idx_visibility_leads_created_at ON visibility_leads(created_at DESC);

-- Enable Row Level Security (optional, for production)
ALTER TABLE visibility_leads ENABLE ROW LEVEL SECURITY;

-- Allow insert for API (adjust as needed for your security model)
-- You may want to use service role key for backend
