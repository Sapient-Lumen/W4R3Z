theory P0_Authority_Propose_Refinement
  imports P0_Authority_Sequence
begin

text \<open>
  One Epoch Zero PROPOSE value transformer.  The definitions name the same
  first-failure order used by the hosted C++20 specimen: scope, structural
  validity, duplicate identifier, fixed capacity, finite sequence, acceptance.
  An accepted command installs exactly one selected abstract proposal and
  advances exactly once; every non-accepted decision frames the whole context.

  Natural numbers plus explicit 16/64-bit bounds are a proof value image.  This
  theory does not import C++ source semantics, object layout, compiler semantics,
  concurrency, persistence, allocation, or ABI facts.  The C++ snapshot relation
  and mutation-rejecting executable checker are separate evidence layers.
\<close>

datatype p0_value_operation =
    P0_Value_Propose
  | P0_Value_Other

datatype p0_value_action =
    P0_Value_Increment
  | P0_Value_Other_Action

datatype p0_propose_decision =
    P0_Propose_Out_Of_Scope
  | P0_Propose_Invalid
  | P0_Propose_Duplicate
  | P0_Propose_Capacity
  | P0_Propose_Sequence_Exhausted
  | P0_Propose_Accepted

record p0_propose_command =
  p0_propose_operation :: p0_value_operation
  p0_propose_actor :: nat
  p0_propose_id :: nat
  p0_propose_subject :: nat
  p0_propose_resource :: nat
  p0_propose_action :: p0_value_action
  p0_propose_amount :: nat

record p0_propose_context =
  p0_propose_known_ids :: "nat set"
  p0_propose_count :: nat
  p0_propose_sequence_state :: p0_sequenced_authority_state

definition p0_u16_valid :: "nat \<Rightarrow> bool" where
  "p0_u16_valid value \<longleftrightarrow> value < 2 ^ 16"

definition p0_u64_valid :: "nat \<Rightarrow> bool" where
  "p0_u64_valid value \<longleftrightarrow> value < 2 ^ 64"

definition p0_proposal_capacity :: nat where
  "p0_proposal_capacity = 8"

definition p0_resource_capacity :: nat where
  "p0_resource_capacity = 4"

definition p0_propose_command_valid :: "p0_propose_command \<Rightarrow> bool" where
  "p0_propose_command_valid command \<longleftrightarrow>
     p0_u16_valid (p0_propose_id command) \<and>
     p0_propose_id command \<noteq> 0 \<and>
     p0_u16_valid (p0_propose_actor command) \<and>
     p0_propose_actor command \<noteq> 0 \<and>
     p0_u16_valid (p0_propose_subject command) \<and>
     p0_propose_actor command = p0_propose_subject command \<and>
     p0_u16_valid (p0_propose_resource command) \<and>
     p0_propose_resource command < p0_resource_capacity \<and>
     p0_propose_action command = P0_Value_Increment \<and>
     p0_u64_valid (p0_propose_amount command) \<and>
     p0_propose_amount command \<noteq> 0"

definition p0_propose_context_valid :: "p0_propose_context \<Rightarrow> bool" where
  "p0_propose_context_valid context \<longleftrightarrow>
     finite (p0_propose_known_ids context) \<and>
     p0_propose_count context = card (p0_propose_known_ids context) \<and>
     p0_propose_count context \<le> p0_proposal_capacity \<and>
     (\<forall>identifier \<in> p0_propose_known_ids context.
        p0_u16_valid identifier \<and> identifier \<noteq> 0) \<and>
     finite_sequence_valid
       (p0_sequence_value (p0_propose_sequence_state context))"

definition p0_proposal_of :: "p0_propose_command \<Rightarrow> p0_proposal" where
  "p0_proposal_of command =
     \<lparr>p0_proposal_subject = p0_propose_subject command,
      p0_proposal_resource = p0_propose_resource command,
      p0_proposal_action = P0_Increment,
      p0_proposal_amount = p0_propose_amount command,
      p0_proposal_consumed = False\<rparr>"

definition p0_propose_first_failure ::
  "p0_propose_context \<Rightarrow> p0_propose_command \<Rightarrow> p0_propose_decision" where
  "p0_propose_first_failure context command =
     (if p0_propose_operation command \<noteq> P0_Value_Propose then
        P0_Propose_Out_Of_Scope
      else if \<not> p0_propose_command_valid command then
        P0_Propose_Invalid
      else if p0_propose_id command \<in> p0_propose_known_ids context then
        P0_Propose_Duplicate
      else if p0_proposal_capacity \<le> p0_propose_count context then
        P0_Propose_Capacity
      else if \<not> p0_sequence_accepts (p0_propose_sequence_state context) then
        P0_Propose_Sequence_Exhausted
      else
        P0_Propose_Accepted)"

definition p0_propose_register ::
  "p0_propose_context \<Rightarrow> p0_propose_command \<Rightarrow> p0_propose_context" where
  "p0_propose_register context command =
     (let transition =
        p0_sequence_transition
          (\<lambda>state. p0_register_proposal state (p0_proposal_of command))
          (p0_propose_sequence_state context)
      in context\<lparr>
           p0_propose_known_ids :=
             insert (p0_propose_id command) (p0_propose_known_ids context),
           p0_propose_count := Suc (p0_propose_count context),
           p0_propose_sequence_state := snd transition\<rparr>)"

definition p0_propose_step ::
  "p0_propose_context \<Rightarrow> p0_propose_command \<Rightarrow>
   p0_propose_decision \<times> p0_propose_context" where
  "p0_propose_step context command =
     (let decision = p0_propose_first_failure context command
      in if decision = P0_Propose_Accepted then
           (decision, p0_propose_register context command)
         else
           (decision, context))"

theorem p0_propose_out_of_scope_precedes_all:
  assumes "p0_propose_operation command \<noteq> P0_Value_Propose"
  shows "p0_propose_first_failure context command = P0_Propose_Out_Of_Scope"
  using assms by (simp add: p0_propose_first_failure_def)

theorem p0_propose_invalid_precedes_duplicate_capacity_sequence:
  assumes "p0_propose_operation command = P0_Value_Propose"
      and "\<not> p0_propose_command_valid command"
  shows "p0_propose_first_failure context command = P0_Propose_Invalid"
  using assms by (simp add: p0_propose_first_failure_def)

theorem p0_propose_duplicate_precedes_capacity_sequence:
  assumes "p0_propose_operation command = P0_Value_Propose"
      and "p0_propose_command_valid command"
      and "p0_propose_id command \<in> p0_propose_known_ids context"
  shows "p0_propose_first_failure context command = P0_Propose_Duplicate"
  using assms by (simp add: p0_propose_first_failure_def)

theorem p0_propose_capacity_precedes_sequence:
  assumes "p0_propose_operation command = P0_Value_Propose"
      and "p0_propose_command_valid command"
      and "p0_propose_id command \<notin> p0_propose_known_ids context"
      and "p0_proposal_capacity \<le> p0_propose_count context"
  shows "p0_propose_first_failure context command = P0_Propose_Capacity"
  using assms by (simp add: p0_propose_first_failure_def)

theorem p0_propose_terminal_is_first_remaining_failure:
  assumes "p0_propose_operation command = P0_Value_Propose"
      and "p0_propose_command_valid command"
      and "p0_propose_id command \<notin> p0_propose_known_ids context"
      and "p0_propose_count context < p0_proposal_capacity"
      and "p0_sequence_value (p0_propose_sequence_state context) =
             accepted_sequence_terminal"
  shows
    "p0_propose_first_failure context command =
       P0_Propose_Sequence_Exhausted"
  using assms
  by (simp add: p0_propose_first_failure_def p0_sequence_accepts_def
                finite_sequence_available_def)

theorem p0_propose_accepted_iff_all_guards_pass:
  "p0_propose_first_failure context command = P0_Propose_Accepted \<longleftrightarrow>
   p0_propose_operation command = P0_Value_Propose \<and>
   p0_propose_command_valid command \<and>
   p0_propose_id command \<notin> p0_propose_known_ids context \<and>
   p0_propose_count context < p0_proposal_capacity \<and>
   p0_sequence_accepts (p0_propose_sequence_state context)"
  by (auto simp: p0_propose_first_failure_def split: if_splits)

theorem p0_propose_denial_frames_exact_context:
  assumes decision:
    "p0_propose_first_failure context command = decision"
      and denied: "decision \<noteq> P0_Propose_Accepted"
  shows "p0_propose_step context command = (decision, context)"
  using decision denied by (simp add: p0_propose_step_def)

theorem p0_propose_accepted_inserts_exact_identifier:
  assumes accepted:
    "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_propose_known_ids (snd (p0_propose_step context command)) =
       insert (p0_propose_id command) (p0_propose_known_ids context)"
  using accepted
  by (simp add: p0_propose_step_def p0_propose_register_def)

theorem p0_propose_accepted_increments_count_once:
  assumes accepted:
    "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_propose_count (snd (p0_propose_step context command)) =
       Suc (p0_propose_count context)"
  using accepted
  by (simp add: p0_propose_step_def p0_propose_register_def)

theorem p0_propose_accepted_advances_sequence_once:
  assumes accepted:
    "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_sequence_value
       (p0_propose_sequence_state (snd (p0_propose_step context command))) =
     Suc (p0_sequence_value (p0_propose_sequence_state context))"
proof -
  from accepted have available:
    "p0_sequence_accepts (p0_propose_sequence_state context)"
    by (simp add: p0_propose_accepted_iff_all_guards_pass)
  with accepted show ?thesis
    by (simp add: p0_propose_step_def p0_propose_register_def
                  p0_sequence_transition_def)
qed

theorem p0_propose_accepted_installs_exact_selected_proposal:
  assumes accepted:
    "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_state_proposal
       (p0_sequence_authority
         (p0_propose_sequence_state (snd (p0_propose_step context command)))) =
     p0_proposal_of command"
proof -
  from accepted have available:
    "p0_sequence_accepts (p0_propose_sequence_state context)"
    by (simp add: p0_propose_accepted_iff_all_guards_pass)
  with accepted show ?thesis
    by (simp add: p0_propose_step_def p0_propose_register_def
                  p0_sequence_transition_def p0_register_proposal_def)
qed

theorem p0_propose_accepted_preserves_lease_and_counter:
  assumes accepted:
    "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_state_lease
       (p0_sequence_authority
         (p0_propose_sequence_state (snd (p0_propose_step context command)))) =
     p0_state_lease
       (p0_sequence_authority (p0_propose_sequence_state context)) \<and>
     p0_state_counter
       (p0_sequence_authority
         (p0_propose_sequence_state (snd (p0_propose_step context command)))) =
     p0_state_counter
       (p0_sequence_authority (p0_propose_sequence_state context))"
proof -
  from accepted have available:
    "p0_sequence_accepts (p0_propose_sequence_state context)"
    by (simp add: p0_propose_accepted_iff_all_guards_pass)
  with accepted show ?thesis
    by (simp add: p0_propose_step_def p0_propose_register_def
                  p0_sequence_transition_def p0_register_proposal_def)
qed

theorem p0_propose_accepted_preserves_context_validity:
  assumes valid: "p0_propose_context_valid context"
      and accepted:
        "p0_propose_first_failure context command = P0_Propose_Accepted"
  shows
    "p0_propose_context_valid (snd (p0_propose_step context command))"
proof -
  from accepted have guards:
    "p0_propose_operation command = P0_Value_Propose \<and>
     p0_propose_command_valid command \<and>
     p0_propose_id command \<notin> p0_propose_known_ids context \<and>
     p0_propose_count context < p0_proposal_capacity \<and>
     p0_sequence_accepts (p0_propose_sequence_state context)"
    by (simp add: p0_propose_accepted_iff_all_guards_pass)
  then have available:
    "finite_sequence_available
       (p0_sequence_value (p0_propose_sequence_state context))"
    by (simp add: p0_sequence_accepts_def)
  then have advance:
    "finite_sequence_advance
       (p0_sequence_value (p0_propose_sequence_state context)) =
     Some (Suc (p0_sequence_value (p0_propose_sequence_state context)))"
    by (rule finite_sequence_advance_if_available)
  then have next_valid:
    "finite_sequence_valid
       (Suc (p0_sequence_value (p0_propose_sequence_state context)))"
    using finite_sequence_advance_success by blast
  from valid guards next_valid accepted show ?thesis
    by (auto simp: p0_propose_context_valid_def
                   p0_propose_command_valid_def
                   p0_propose_step_def p0_propose_register_def
                   p0_sequence_transition_def)
qed

end
