import streamlit as st

from pawpal_system import Priority, Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Daily time budget (minutes)", min_value=0, max_value=600, value=60
)

# Create the Owner/Scheduler once per session, then reuse across reruns.
if "owner" not in st.session_state:
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.scheduler = Scheduler(owner=owner)
    st.session_state.owner = owner

owner = st.session_state.owner

# Keep the persisted owner in sync with the current inputs.
owner.name = owner_name
owner.set_available_minutes(int(available_minutes))

st.markdown("### Pets")
st.caption("Add a pet. Each stays in memory for the whole session.")

pcol1, pcol2, pcol3 = st.columns(3)
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pcol2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pcol3:
    pet_age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species, age=int(pet_age)))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.get_tasks())}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks to a pet. They feed directly into your scheduler.")

if not owner.pets:
    st.info("Add a pet first, then you can add tasks to it.")
else:
    target_pet_name = st.selectbox(
        "Add task to which pet?", [p.name for p in owner.pets]
    )
    pet = next(p for p in owner.pets if p.name == target_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        recurrence = st.selectbox("Recurrence", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet.add_task(
            Task(
                name=task_title,
                duration_minutes=int(duration),
                priority=Priority[priority.upper()],
                recurrence=recurrence,
            )
        )

tasks = owner.all_tasks()
if tasks:
    st.write("Current tasks:")

    # Filter + sort controls, backed by the Scheduler's own methods.
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        status_filter = st.selectbox("Show", ["all", "pending", "completed"])
    with fcol2:
        pet_filter = st.selectbox("Pet", ["all"] + [p.name for p in owner.pets])
    with fcol3:
        sort_mode = st.selectbox("Sort by", ["priority", "start time"])

    completed_arg = {"all": None, "pending": False, "completed": True}[status_filter]
    filtered = owner.scheduler.filter_tasks(
        completed=completed_arg,
        pet_name=None if pet_filter == "all" else pet_filter,
    )
    if sort_mode == "priority":
        filtered = owner.scheduler.sort_by_priority(filtered)
    else:
        filtered = owner.scheduler.sort_by_time(filtered)

    # Map each task back to its pet name for display.
    pet_of = {id(t): p.name for p in owner.pets for t in p.get_tasks()}

    if filtered:
        st.table(
            [
                {
                    "Pet": pet_of.get(id(t), "—"),
                    "Title": t.name,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority.name,
                    "Recurrence": t.recurrence,
                    "Status": "✅ done" if t.completed else "⏳ pending",
                }
                for t in filtered
            ]
        )
    else:
        st.info("No tasks match the current filters.")

    # Completion controls (kept interactive; the table above is read-only).
    st.caption("Mark tasks complete:")
    for pi, p in enumerate(owner.pets):
        for ti, t in enumerate(p.get_tasks()):
            if t.completed:
                continue
            c = st.columns([5, 2])
            c[0].write(f"{p.name} — {t.name} ({t.priority.name}, {t.duration_minutes} min)")
            if c[1].button("Complete", key=f"complete_{pi}_{ti}"):
                nxt = p.complete_task(t)
                if nxt is not None:
                    st.success(f"Completed '{t.name}' — added next {t.recurrence} occurrence.")
                else:
                    st.success(f"Completed '{t.name}'.")
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Prioritizes tasks and fits them within the owner's daily time budget.")

if st.button("Generate schedule"):
    # Surface any scheduling conflicts before showing the plan.
    conflicts = owner.scheduler.detect_conflicts()
    for warning in conflicts:
        st.warning(warning)

    plan = owner.scheduler.build_plan()
    if not plan:
        st.info("No tasks fit today's schedule. Add tasks or raise the time budget.")
    else:
        used = sum(t.duration_minutes for t in plan)
        budget = owner.available_minutes
        st.success(
            f"Scheduled {len(plan)} task(s) — using {used}/{budget} min "
            f"({budget - used} min free)."
        )
        st.write("Today's plan:")
        st.table(
            [
                {
                    "Order": i,
                    "Title": t.name,
                    "Priority": t.priority.name,
                    "Duration": f"{t.duration_minutes} min",
                }
                for i, t in enumerate(plan, 1)
            ]
        )
        if not conflicts:
            st.caption("✅ No scheduling conflicts detected.")
