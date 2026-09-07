import sqlite3
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "tareas.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente'
            )
            """
        )


def add_task(titulo: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tareas (titulo, estado) VALUES (?, 'pendiente')",
            (titulo,),
        )


def list_tasks() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, titulo, estado FROM tareas ORDER BY id DESC"
        ).fetchall()


def toggle_status(task_id: int, estado_actual: str) -> None:
    nuevo_estado = "finalizada" if estado_actual == "pendiente" else "pendiente"
    with get_connection() as conn:
        conn.execute(
            "UPDATE tareas SET estado = ? WHERE id = ?",
            (nuevo_estado, task_id),
        )


def delete_task(task_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tareas WHERE id = ?", (task_id,))


def main() -> None:
    st.set_page_config(page_title="Mi Organizador", layout="centered")
    init_db()

    st.title("Mi Organizador")
    st.caption("Gestión de tareas con Streamlit y SQLite")

    with st.form("nueva_tarea", clear_on_submit=True):
        titulo = st.text_input("Nueva tarea", placeholder="Ej: Comprar pan")
        submitted = st.form_submit_button("Agregar")
        if submitted:
            texto = titulo.strip()
            if texto:
                add_task(texto)
                st.rerun()
            else:
                st.warning("Escribí una descripción para la tarea.")

    st.subheader("Tareas")
    tareas = list_tasks()

    if not tareas:
        st.info("No hay tareas todavía. Agregá la primera arriba.")
        return

    header = st.columns([0.5, 3.2, 1.4, 1.7, 1.1])
    header[0].markdown("**#**")
    header[1].markdown("**Tarea**")
    header[2].markdown("**Estado**")
    header[3].markdown("**Cambiar**")
    header[4].markdown("**Borrar**")

    for tarea in tareas:
        cols = st.columns([0.5, 3.2, 1.4, 1.7, 1.1])
        cols[0].write(tarea["id"])
        cols[1].write(tarea["titulo"])
        cols[2].write(tarea["estado"].capitalize())

        etiqueta = (
            "Finalizar" if tarea["estado"] == "pendiente" else "Reabrir"
        )
        if cols[3].button(etiqueta, key=f"toggle_{tarea['id']}"):
            toggle_status(tarea["id"], tarea["estado"])
            st.rerun()

        if cols[4].button("Borrar", key=f"delete_{tarea['id']}"):
            delete_task(tarea["id"])
            st.rerun()


if __name__ == "__main__":
    main()
