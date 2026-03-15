use std::path::Path;
use std::process::Command;
use tauri::Manager;

fn python_dir() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("Could not resolve project root")
        .join("python")
}

/// In debug builds: invokes the feature's main.py via the venv Python.
/// In release builds: invokes the bundled executable from Tauri's resource directory.
fn invoke_python(
    app: &tauri::AppHandle,
    feature: &str,
    args: &[&str],
) -> Result<std::process::Output, String> {
    let mut cmd = make_command(app, feature);
    for arg in args {
        cmd.arg(arg);
    }
    cmd.output()
        .map_err(|e| format!("Kon Python niet starten: {e}"))
}

#[cfg(debug_assertions)]
fn make_command(_app: &tauri::AppHandle, feature: &str) -> Command {
    let python = python_dir();

    #[cfg(windows)]
    let python_bin = python.join(".venv").join("Scripts").join("python.exe");
    #[cfg(not(windows))]
    let python_bin = python.join(".venv").join("bin").join("python3");

    let mut cmd = Command::new(python_bin);
    cmd.arg(python.join(feature).join("main.py"));
    cmd.current_dir(&python);
    cmd
}

#[cfg(not(debug_assertions))]
fn make_command(app: &tauri::AppHandle, feature: &str) -> Command {
    let exe_name = format!("{}{}", feature, std::env::consts::EXE_SUFFIX);

        let exe_path = app
            .path()
            .resource_dir()
            .expect("Could not resolve resource directory")
            .join("_up_")
            .join("python")
            .join("dist")
            .join(&exe_name);

        Command::new(exe_path)
}

fn handle_output(output: std::process::Output) -> Result<String, String> {
    if output.status.success() {
        return Ok(String::from_utf8_lossy(&output.stdout).trim().to_string());
    }
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    Err(if !stdout.is_empty() { stdout } else { stderr })
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn get_archives(app: tauri::AppHandle) -> Result<String, String> {
    let output = invoke_python(&app, "get_archive_overview", &[])?;
    handle_output(output)
}

#[tauri::command]
fn create_archive(app: tauri::AppHandle, name: String, path: String) -> Result<(), String> {
    let output = invoke_python(&app, "create_new_archive", &[&name, &path])?;
    handle_output(output).map(|_| ())
}

#[tauri::command]
fn run_database_migrations(app: tauri::AppHandle) -> Result<String, String> {
    // Get the resource directory
        let resource_dir = app
            .path()
            .resource_dir()
            .expect("Could not get resource directory");

        let python_dir = resource_dir
            .join("_up_")
            .join("python");

        let python_dir_str = python_dir
            .to_str()
            .ok_or("Invalid path")?;

        // Pass the python directory as an argument
        let output = invoke_python(&app, "run_migrations", &[python_dir_str])?;
        handle_output(output)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let app_handle = app.handle().clone();

            // Run migrations in background thread
            std::thread::spawn(move || {
                match run_database_migrations(app_handle) {
                    Ok(result) => println!("✅ Migrations: {}", result),
                    Err(e) => eprintln!("⚠️ Migration failed: {}", e),
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, create_archive, get_archives, run_database_migrations])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
