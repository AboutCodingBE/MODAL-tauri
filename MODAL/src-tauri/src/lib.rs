use std::path::Path;
use std::process::Command;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Resolves the project root at compile time from the Cargo manifest directory.
/// src-tauri/ is one level below the project root, so we go up one directory.
fn python_dir() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("Could not resolve project root")
        .join("python")
}

#[tauri::command]
fn get_archives() -> Result<String, String> {
    let python = python_dir();
    let script = python.join("get_archive_overview").join("main.py");

    let output = Command::new("python3")
        .arg(&script)
        .current_dir(&python)
        .output()
        .map_err(|e| format!("Kon Python niet starten: {e}"))?;

    if output.status.success() {
        return Ok(String::from_utf8_lossy(&output.stdout).trim().to_string());
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    Err(if !stdout.is_empty() { stdout } else { stderr })
}

#[tauri::command]
fn create_archive(name: String, path: String) -> Result<(), String> {
    let python = python_dir();
    let script = python.join("create_new_archive").join("main.py");

    let output = Command::new("python3")
        .arg(&script)
        .arg(&name)
        .arg(&path)
        .current_dir(&python)
        .output()
        .map_err(|e| format!("Kon Python niet starten: {e}"))?;

    if output.status.success() {
        return Ok(());
    }

    // Prefer stdout (business-logic error) over stderr (Python traceback)
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    Err(if !stdout.is_empty() { stdout } else { stderr })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![greet, create_archive, get_archives])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
