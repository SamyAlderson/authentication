// models.py

use std::env;
use std::path::Path;

use sqlx::{Connection, SqlitePool};
use bcrypt::{Bcrypt, hash};
use serde::{Serialize, Deserialize};

// database models
#[derive(Serialize, Deserialize)]
struct User {
    id: i32,
    username: String,
    password_hash: String,
}

#[derive(Serialize, Deserialize)]
struct Session {
    id: i32,
    user_id: i32,
    token: String,
}

// db connections
async fn create_db_pool() -> SqlitePool {
    let db_file = env::var("DB_FILE").unwrap();
    let db_path = Path::new(&db_file);
    sqlx::sqlite::SqlitePool::connect(format!("file:{}?mode=rwc", db_path.display()).as_str()).await.unwrap()
}

async fn db_pool() -> SqlitePool {
    let db_pool = create_db_pool();
    db_pool
}

// user model stuff
async fn create_user(username: String, password: String) -> Result<(), sqlx::Error> {
    let db_pool = db_pool().await;
    let mut conn = db_pool.acquire().await?;

    let hashed_password = hash(&password, 12).unwrap();

    sqlx::query("INSERT INTO users (username, password_hash) VALUES ($1, $2)")
        .bind(username)
        .bind(hashed_password)
        .execute(&mut conn)
        .await?;

    Ok(())
}

async fn get_user(username: String) -> Option<User> {
    let db_pool = db_pool().await;
    let conn = db_pool.acquire().await?;

    let row = sqlx::query("SELECT id, username, password_hash FROM users WHERE username = $1")
        .bind(username)
        .fetch_one(&conn)
        .await?;

    Some(User {
        id: row.get(0),
        username: row.get(1),
        password_hash: row.get(2),
    })
}

// session model stuff
async fn create_session(user_id: i32) -> Result<(), sqlx::Error> {
    let db_pool = db_pool().await;
    let mut conn = db_pool.acquire().await?;

    sqlx::query("INSERT INTO sessions (user_id, token) VALUES ($1, $2)")
        .bind(user_id)
        .bind(uuid::Uuid::new_v4().to_string())
        .execute(&mut conn)
        .await?;

    Ok(())
}

async fn get_session(token: String) -> Option<Session> {
    let db_pool = db_pool().await;
    let conn = db_pool.acquire().await?;

    let row = sqlx::query("SELECT id, user_id, token FROM sessions WHERE token = $1")
        .bind(token)
        .fetch_one(&conn)
        .await?;

    Some(Session {
        id: row.get(0),
        user_id: row.get(1),
        token: row.get(2),
    })
}
```
```rust
// tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    async fn test_create_user() {
        let username = "test_user".to_string();
        let password = "test_password".to_string();

        create_user(username.clone(), password.clone()).await.unwrap();

        let got_user = get_user(username.clone()).await.unwrap();
        assert_eq!(got_user.username, username);
    }

    #[test]
    async fn test_create_session() {
        let user_id = 1;

        create_session(user_id).await.unwrap();

        let got_session = get_session("some_token".to_string()).await;
        assert!(got_session.is_none());
    }
}