CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  balance NUMERIC(18,8) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE deposit_addresses (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  address TEXT UNIQUE NOT NULL,
  currency TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE deposits (
  id BIGSERIAL PRIMARY KEY,
  address_id BIGINT REFERENCES deposit_addresses(id) ON DELETE SET NULL,
  tx_hash TEXT UNIQUE,
  amount NUMERIC(18,8),
  currency TEXT,
  confirmed BOOLEAN DEFAULT FALSE,
  detected_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE bets (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  bet_amount NUMERIC(18,8) NOT NULL,
  choice TEXT NOT NULL,
  choice_text TEXT,
  result_value TEXT,
  win BOOLEAN,
  profit NUMERIC(18,8),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE payouts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  amount NUMERIC(18,8) NOT NULL,
  currency TEXT NOT NULL,
  to_address TEXT NOT NULL,
  tx_hash TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  processed_at TIMESTAMP WITH TIME ZONE
);
