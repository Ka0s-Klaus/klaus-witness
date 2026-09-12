import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from core.database import SessionLocal, init_db
from core.models import User, Event, Memory, Persona, EventType, ConsentLevel

def seed_users():
    """Crear usuarios ficticios pero realistas"""
    db = SessionLocal()
    init_db()

    users_data = [
        {
            "email": "sophia@testigo.local",
            "username": "sophia",
            "first_name": "Sophia",
            "last_name": "García",
        },
        {
            "email": "marcus@testigo.local",
            "username": "marcus",
            "first_name": "Marcus",
            "last_name": "Chen",
        },
        {
            "email": "elena@testigo.local",
            "username": "elena",
            "first_name": "Elena",
            "last_name": "Rodriguez",
        }
    ]

    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                id=uuid4(),
                email=user_data["email"],
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password_hash="dummy",
                is_active=True
            )
            db.add(user)

    db.commit()
    return db.query(User).all()

def seed_events(users):
    """Crear eventos realistas para cada usuario"""
    db = SessionLocal()

    events_templates = {
        "sophia": [
            ("2024-01-15", EventType.DECISION, "Decidí dejar mi trabajo en consultoría después de 5 años. La presión era insostenible pero tenía miedo de no encontrar nada mejor."),
            ("2024-02-03", EventType.REFLECTION, "Reflexionando: siempre he sido perfeccionista. ¿Es eso una fortaleza o una carga? Mis amigos dicen que nunca me doy paz."),
            ("2024-02-20", EventType.EMOTION, "Hoy tuve miedo. Verdadero miedo. Sin ingresos, sin red de seguridad. Pero también una pequeña chispa de libertad que no había sentido en años."),
            ("2024-03-10", EventType.FACT, "Empecé un proyecto freelance con dos colegas. Primer cliente: una startup. No es mucho, pero es mío."),
            ("2024-03-25", EventType.DECISION, "Decidí viajar a Japón sola. A los 32, no creí que lo haría. Pero aquí estoy, en Tokio, sin agenda."),
            ("2024-04-05", EventType.HITO_VITAL, "Conocí a alguien en Kioto. No fue lo que busqué. Pero a veces lo mejor llega cuando no buscas."),
            ("2024-04-15", EventType.EMOTION, "Llamé a mi madre. Le conté sobre el viaje, el proyecto, la persona. Lloró. De orgullo, creo."),
        ],
        "marcus": [
            ("2024-01-08", EventType.FACT, "Fui diagnosticado con ansiedad. Después de años negándolo. La aceptación fue más fácil que esperaba."),
            ("2024-01-25", EventType.DECISION, "Empecé terapia. Algo que debería haber hecho hace una década."),
            ("2024-02-14", EventType.REFLECTION, "¿Cuántas oportunidades perdí por miedo? Innumerables. Pero es hora de contar las que ganaré a partir de hoy."),
            ("2024-03-01", EventType.EMOTION, "Mi hermana dijo: 'Veo cómo te estás transformando'. Eso me rompió y sanó al mismo tiempo."),
            ("2024-03-15", EventType.FACT, "Aprendí a programar en Python. Pequeño hito. Pero es mío."),
            ("2024-04-10", EventType.DECISION, "Decidí contactar a mi mejor amigo del que no hablé en 3 años. El orgullo es un precio caro."),
            ("2024-04-20", EventType.HITO_VITAL, "Recibí el llamado para trabajar como junior developer. No es grande, pero es un comienzo."),
        ],
        "elena": [
            ("2024-01-02", EventType.FACT, "Mi hija entró a la universidad. La casa está vacía ahora. No sé quién soy sin ser mamá a tiempo completo."),
            ("2024-01-20", EventType.REFLECTION, "40 años y redescubriéndome. ¿Será demasiado tarde para perseguir los sueños que pospuse?"),
            ("2024-02-08", EventType.DECISION, "Volveré a la universidad. Antropología. Siempre lo quise pero 'no había tiempo'."),
            ("2024-02-28", EventType.EMOTION, "Mi exmarido se enteró de mi decisión. Dijo 'Siempre supe que eras más que suficiente para ti sola'."),
            ("2024-03-12", EventType.FACT, "Primer día de clases. Me siento como una impostora entre gente 20 años menor. Y también invencible."),
            ("2024-04-05", EventType.DECISION, "Acepté salir con alguien del seminario. 6 meses sin citas. Estoy nerviosa y emocionada."),
            ("2024-04-18", EventType.HITO_VITAL, "Mi hija vino de visita. Vio mis notas, conoció a mis nuevos amigos. Dijo: 'Mamá, estoy orgullosa de ti'."),
        ]
    }

    for user in users:
        username = user.username
        if username in events_templates:
            for date_str, event_type, content in events_templates[username]:
                event_date = datetime.fromisoformat(f"{date_str}T10:00:00")

                event = Event(
                    id=uuid4(),
                    user_id=user.id,
                    timestamp=event_date,
                    event_type=event_type,
                    content=content,
                    context={"lugar": "personal", "etapa_vital": "autodescubrimiento"},
                    emotional_weight=0.6,
                    consent_level=ConsentLevel.PERSONAL,
                    consent_granted_at=event_date
                )
                db.add(event)

    db.commit()

def seed_memories(users):
    """Crear memorias semánticas consolidadas"""
    db = SessionLocal()

    memories_by_user = {
        "sophia": [
            ("Valora la autenticidad y la libertad personal", "valor", 0.85),
            ("Tiende a ser perfeccionista y autoexigente", "patron", 0.78),
            ("Es capaz de tomar decisiones difíciles", "patron", 0.82),
            ("Busca conexiones significativas", "patrón", 0.71),
            ("Tiene miedo al fracaso pero actúa a pesar de ello", "temor", 0.75),
        ],
        "marcus": [
            ("Lucha con la ansiedad pero está aprendiendo a manejarla", "patron", 0.68),
            ("Valora la honestidad consigo mismo", "valor", 0.89),
            ("Está en transición de carrera", "patron", 0.80),
            ("Mantiene relaciones significativas a pesar de los desafíos", "relacion", 0.72),
            ("Es más fuerte de lo que se da crédito", "creencia", 0.76),
        ],
        "elena": [
            ("Nunca es demasiado tarde para empezar de nuevo", "creencia", 0.88),
            ("Valora el aprendizaje continuo", "valor", 0.92),
            ("Es resiliente y adaptable", "patron", 0.85),
            ("La maternidad fue central pero no es su única identidad", "reflection", 0.79),
            ("Desea vivir plenamente, no solo existir", "objetivo", 0.86),
        ]
    }

    for user in users:
        username = user.username
        if username in memories_by_user:
            for belief, category, confidence in memories_by_user[username]:
                memory = Memory(
                    id=uuid4(),
                    user_id=user.id,
                    belief=belief,
                    category=category,
                    confidence=confidence,
                    status="activa",
                    first_seen=datetime.utcnow() - timedelta(days=30),
                    last_confirmed=datetime.utcnow() - timedelta(days=2),
                    version=1
                )
                db.add(memory)

    db.commit()

def seed_personas(users):
    """Crear personas versionadas"""
    db = SessionLocal()

    for user in users:
        persona = Persona(
            id=uuid4(),
            user_id=user.id,
            version=1,
            temporal_range_start=datetime.utcnow() - timedelta(days=120),
            summary=f"Versión 1 de {user.first_name}: en transición, buscando autenticidad y crecimiento personal.",
            values=["autenticidad", "crecimiento", "libertad"],
            patterns=["reflexión frecuente", "acción a pesar del miedo"],
            contradictions=["desea seguridad pero busca libertad"],
            voice_samples=[
                "No sé exactamente qué busco, pero sé que es algo diferente.",
                "El miedo existe, pero no me detiene.",
                "Esta es mi historia, y finalmente estoy escribiéndola como quiero."
            ],
            is_active=True
        )
        db.add(persona)

    db.commit()
    print("✓ Datos ficticios cargados: 3 usuarios, ~7 eventos cada uno, 5+ memorias, personas versionadas")

if __name__ == "__main__":
    print("Sembrando base de datos con datos ficticios realistas...")
    users = seed_users()
    print(f"✓ {len(users)} usuarios creados")

    seed_events(users)
    print("✓ Eventos creados")

    seed_memories(users)
    print("✓ Memorias creadas")

    seed_personas(users)
    print("✓ Personas versionadas creadas")

    print("\n=== Sistema listo para usar ===")
    print("Usuarios de prueba:")
    for user in users:
        print(f"  - {user.username} ({user.email})")
