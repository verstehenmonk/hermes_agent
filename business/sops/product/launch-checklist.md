# SOP: Launch Checklist

Run before any user-facing launch. Each item is green / yellow / red. Reds
block the launch.

## Product
- [ ] Spec is `approved` in Notion
- [ ] All Linear issues in the epic are `done`
- [ ] Telemetry events are firing in production for ≥ 24h
- [ ] One internal user (founder) has used the feature end-to-end

## Engineering
- [ ] CI is green on the launch commit
- [ ] Deploy is verified per `sops/engineering/release.md`
- [ ] Feature flag exists if the feature is reversible
- [ ] Rollback plan documented per `sops/engineering/deploy-rollback.md`

## Marketing
- [ ] Blog post DRAFT in `#marketing`
- [ ] X thread DRAFT in `#marketing`
- [ ] LinkedIn post DRAFT in `#marketing`
- [ ] Customer email DRAFT in `#marketing`
- [ ] Pricing page updated (if pricing changes)

## CS
- [ ] FAQ entries drafted in Notion
- [ ] Support macros updated for likely questions
- [ ] CS team (= founder) briefed on the change

## Output

Produce a go/no-go table in `#cos`. Founder makes the call. Never auto-launch.
