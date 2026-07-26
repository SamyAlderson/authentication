// auth.py

use std::collections::HashMap;

// Import required libraries
use bcrypt::Bcrypt;
use jsonwebtoken::{encode, decode, Header, EncodingKey, Validation};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, PgPoolOptions};

// Import custom modules
use crate::models::{User, Session};
use crate::schemas::{UserSchema, SessionSchema};

// Configuration settings
const SECRET_KEY: &str = "secret_key_here";
const EXPIRES_IN: i64 = 3600; // 1 hour

// Authentication error type
#[derive(Debug)]
enum AuthError {
    IncorrectPassword,
    UserNotExists,
    SessionExpired,
}

impl std::error::Error for AuthError {}

impl std::fmt::Display for AuthError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AuthError::IncorrectPassword => write!(f, "Incorrect password"),
            AuthError::UserNotExists => write!(f, "User not exists"),
            AuthError::SessionExpired => write!(f, "Session expired"),
        }
    }
}

// Hash password using bcrypt
fn hash_password(password: &str) -> String {
    let bcrypt = Bcrypt::new();
    bcrypt.hash(password).unwrap()
}

// Verify password using bcrypt
fn verify_password(stored_password: &str, provided_password: &str) -> bool {
    let bcrypt = Bcrypt::new();
    bcrypt.verify(provided_password, stored_password).unwrap()
}

// Generate token
fn generate_token(payload: &str) -> String {
    let header = Header::default();
    let encoding_key = EncodingKey::from_secret(SECRET_KEY.as_bytes());
    let token = encode(&header, payload, &encoding_key).unwrap();
    token
}

// Verify token
fn verify_token(token: &str) -> Result<String, AuthError> {
    let header = Header::default();
    let validation = Validation::default();
    let token = decode(token, &header, &validation).map_err(|_| AuthError::SessionExpired)?;
    let payload = token.claims;
    Ok(payload.to_string())
}

// Register user
pub async fn register_user(
    pool: &PgPool,
    username: String,
    password: String,
) -> Result<(), AuthError> {
    // Check if user already exists
    let user = sqlx::query!("SELECT * FROM users WHERE username = $1", username)
        .fetch_one(pool)
        .await;
    if user.is_some() {
        return Err(AuthError::UserNotExists);
    }

    // Hash password
    let hashed_password = hash_password(&password);

    // Create user
    sqlx::query!(
        "INSERT INTO users (username, password) VALUES ($1, $2)",
        username,
        hashed_password
    )
    .execute(pool)
    .await?;

    Ok(())
}

// Login user
pub async fn login_user(
    pool: &PgPool,
    username: String,
    password: String,
) -> Result<String, AuthError> {
    // Check if user exists
    let user = sqlx::query!("SELECT * FROM users WHERE username = $1", username)
        .fetch_one(pool)
        .await;
    if user.is_none() {
        return Err(AuthError::UserNotExists);
    }

    // Verify password
    if !verify_password(&user.unwrap().password, &password) {
        return Err(AuthError::IncorrectPassword);
    }

    // Generate token
    let payload = jsonwebtoken::encode(
        &Header::default(),
        &json::object! {
            "username" => username,
            "exp" => EXPIRES_IN,
        },
        &SECRET_KEY.as_bytes(),
    )
    .unwrap();

    Ok(payload)
}

// Get user by token
pub async fn get_user_by_token(
    pool: &PgPool,
    token: String,
) -> Result<User, AuthError> {
    // Verify token
    match verify_token(&token) {
        Ok(payload) => {
            // Get user by username
            let user = sqlx::query!("SELECT * FROM users WHERE username = $1", payload)
                .fetch_one(pool)
                .await;
            if user.is_none() {
                return Err(AuthError::UserNotExists);
            }

            Ok(user.unwrap())
        }
        Err(_) => Err(AuthError::SessionExpired),
    }
}

// Delete user by token
pub async fn delete_user_by_token(
    pool: &PgPool,
    token: String,
) -> Result<(), AuthError> {
    // Verify token
    match verify_token(&token) {
        Ok(_) => {
            // Delete user
            sqlx::query!("DELETE FROM users WHERE username = $1", jsonwebtoken::decode::<String>(&token, &SECRET_KEY.as_bytes(), &Validation::default()).unwrap().claims.username).execute(pool).await?;

            Ok(())
        }
        Err(_) => Err(AuthError::SessionExpired),
    }
}