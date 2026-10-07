# Public Link Policy — current

Controlled values for whether a source URL can be exposed in a public layer.

Rows: 9

| public_link_policy | definition | default_action |
| --- | --- | --- |
| public_link_allowed | The link can be public without special boundary note under current review. | allow |
| public_link_allowed_with_boundary_note | The link can be public only with a note blocking safety/completion/referral overclaim. | allow_with_boundary_note |
| boundary_note_required | The link is not inherently barred but sits near risk; public prose must explain the boundary. | manual_review_before_public_link |
| boundary_note_required_or_internal_only | The link may expose family/profile/material near harm; use internal-only unless public link is necessary and reviewed. | prefer_internal_only |
| internal_only_contact_rich | The link exposes contact, support, intake, report/submit, social-media, or referral paths. | do_not_public_link |
| internal_only_case_extractable | The link exposes case rows, names, forensic/legal fields, incident detail, or database extraction paths. | do_not_public_link |
| internal_only_testimony_rich | The link exposes testimony that could be excerpted without governance basis. | do_not_public_link |
| internal_only_image_sensitive | The link exposes images, posters, red-dress material, memorial visuals, vigils, or event maps. | do_not_public_link |
| internal_only_map_or_route_risk | The link exposes routes, coordinates, search fields, living sites, or operational paths. | do_not_public_link |
