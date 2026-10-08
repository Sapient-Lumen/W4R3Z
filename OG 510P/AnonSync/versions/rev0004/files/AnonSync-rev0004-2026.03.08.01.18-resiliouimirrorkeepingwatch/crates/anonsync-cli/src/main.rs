use anonsync_core::{current_posture, recommended_boot_sequence, PROJECT_NAME};

fn main() {
    let posture = current_posture();

    println!("{PROJECT_NAME} workspace scaffold");
    println!("stage: {:?}", posture.stage);
    println!("one_binary_goal: {}", posture.one_binary_goal);
    println!("transport_agnostic_core: {}", posture.transport_agnostic_core);

    println!("bootstrap sequence:");
    for (index, step) in recommended_boot_sequence().iter().enumerate() {
        println!("  {}. {}", index + 1, step);
    }
}
