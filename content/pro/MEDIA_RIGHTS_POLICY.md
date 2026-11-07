# Pro Media Rights Policy

**Applies to:** Pro dua/adhkar videos on `feature/quran-video-pro`.
**Status:** policy baseline only. It does not approve any individual asset or authorize delivery.

## 1. Background video and images

Preferred discovery sources for stock visuals:
- Pexels: https://www.pexels.com/legal-pages/license
- Pixabay: https://pixabay.com/service/license-summary/

Their published licenses generally permit free commercial use and modification without mandatory attribution, subject to restrictions. This is not blanket clearance for every item: identifiable people, trademarks/logos, depicted artwork, property/privacy rights, and misleading endorsement remain separate concerns.

For every downloaded asset, retain:
- exact asset page URL and asset ID (if available);
- creator/uploader name;
- source platform;
- download date;
- license name and a saved copy/link to the applicable terms;
- intended use and edits made;
- any visible people, logos, artwork, or other third-party elements and the resolution of those rights.

Do not scrape or bulk-copy stock libraries. Use individual asset pages or the provider's permitted official API. Avoid identifiable people, prominent logos, branded material, and artwork with unclear rights in the first Pro release.

## 2. Recitation / spoken dua audio

Do not assume that a religious text being old, authentic, or freely accessible makes a particular recording free to reuse. A reciter's performance and recording can carry separate rights.

For every audio recording, require a specific source page and explicit license/permission that covers:
- downloading and editing the recording;
- synchronization with video;
- public posting on social platforms;
- commercial/monetized use if the channel may be monetized;
- the relevant territories and duration, if limited.

Record the performer, recording owner, exact file/page URL, license/permission evidence, attribution wording, and date checked. If any of these are unclear, do not use that recording. No audio asset is currently approved by this policy.

## 3. Per-asset approval gate

A source platform's general license is not enough. Each exact file must pass a per-asset check. Store a rights record beside the asset before it is selected by the renderer. Never treat a stock-library search result or a web page's mere availability as permission.

## 4. Current decision

- Visuals: Pexels and Pixabay are acceptable discovery sources subject to per-asset review and their current restrictions.
- Audio: no provider or recording is pre-approved; verify the exact recording's rights individually.
- No music is to be added. The Pro output should use only the selected dua/adhkar voice recording and permissible ambient/background visuals, unless the user explicitly changes this rule.
- This policy does not authorize a render, Telegram send, or TikTok publication.


## 5. Machine-checkable per-asset evidence contract (required before preview delivery)

A general provider license URL or manifest boolean is not an asset-level clearance. Every exact local media file used by a preview must have one separate JSON rights record under `content/pro/rights/`, with a stable asset ID. The record is a claim/evidence bundle for human review; it is not legal advice and does not itself establish that a license is valid.

### Required common fields

- `schema_version`: integer `1`.
- `asset_id`: stable safe identifier, exactly matching the manifest's asset reference.
- `media_type`: `visual` or `audio`.
- `file_path`: repository-relative path to the exact local asset, confined to the approved Pro media directory; no symlinks.
- `file_sha256`: lowercase SHA-256 of the exact file bytes consumed by the renderer.
- `source_page_url`: exact HTTPS page for this asset/recording, not a provider homepage or search results page.
- `creator_or_performer`, `rights_owner`, `source_platform`, `downloaded_at` (ISO-8601 date/time).
- `license_name` and `license_evidence`: exact applicable license/permission, evidence URL or repository-relative saved evidence file, and SHA-256 when saved locally.
- `intended_uses`: explicit booleans for download, editing, video synchronization, private review delivery, public social posting, and commercial/monetized use. Every use relevant to the planned workflow must be explicitly allowed; unknown/missing is false.
- `territories` and `validity`: permitted territories and any start/end or duration limits; unknown or expired scope blocks use.
- `attribution`: exact required wording, or explicit statement that none is required under the applicable terms.
- `third_party_review`: reviewed flags and resolution notes for identifiable people, logos/trademarks, artwork, property/privacy, and endorsement concerns. Any unresolved issue blocks use.
- `reviewer`, `reviewed_at`, and `decision`: decision must be `approved`; candidate or missing review blocks use.

### Additional audio-only fields

Audio records must also identify the performer and recording owner separately, and explicitly cover download/editing, video synchronization, public social posting, commercial/monetized use where applicable, territories, duration, and attribution. Text authenticity or public-domain status of a dua does not grant rights to a particular performance or recording. Silent videos must not invent or require an audio asset record.

### Validator requirements

The future Pro-only validator must:
1. Resolve each manifest asset reference to exactly one rights record; reject missing, duplicate, orphaned, or mismatched records.
2. Reject path traversal, symlinks, files outside fixed Pro media roots, non-regular files, unknown schema versions, malformed hashes, and any mismatch between recorded and actual SHA-256.
3. Require exact asset page/recording URL, creator/performer, rights owner, source platform, download date, license evidence, reviewer, review date, and an approved decision.
4. Check the specific planned use against the explicit permissions and their territory/time scope; missing or ambiguous evidence fails closed.
5. Recompute the file hash immediately before render and bind the rendered manifest/preview identity to those exact assets.
6. Never treat a boolean such as `rights_verified` or `approved` as a substitute for the evidence record.

No rights record or asset is approved by adding this schema. Each asset remains blocked until its own evidence is collected and human-reviewed.

## 6. Preview destination privacy verification

Before a future preview send, the Pro-only sender must call Telegram Bot API `getChat` using the same bot token and configured chat ID intended for `sendVideo`. Proceed only if the response is successful, the returned `result.id` exactly matches the configured chat ID, and `result.type` is exactly `private`. Reject missing fields, mismatches, groups, supergroups, channels, API errors, and ambiguous responses. Do not infer privacy from a positive numeric ID.

This check must happen in the same isolated send run immediately before the upload, and the verified token/chat pair must be the pair used for the subsequent send. Do not log the bot token or unnecessary personal chat metadata; logs should contain only a redacted outcome such as `private_chat_verified=true`. Add offline mocked tests for success, wrong ID, non-private type, malformed response, API error, and zero `sendVideo` calls on every failed check.

Official API reference: https://core.telegram.org/bots/api#getchat (Chat objects expose a `type` value of `private`, `group`, `supergroup`, or `channel`).


### Implemented enforcement details
- Exact media bytes must live under `assets/pro/media/`; rights records live at `content/pro/rights/{asset_id}.json`; saved license evidence, when used, lives under `content/pro/rights/evidence/`.
- The manifest must reference exactly one visual asset and, for spoken/ambient audio, exactly one audio asset. Silent media must not declare an audio file. The validator rejects mismatched, missing, duplicate, unsafe, symlinked, or out-of-root references and verifies each exact file's SHA-256.
- The current preview/render gate requires worldwide distribution permission, explicit download/edit/synchronization/private-review/public-social/commercial-use permissions, active validity dates, full third-party review notes, and an approved human decision. This is intentionally stricter than private review alone because the candidate is intended for eventual public social use.
- Required attribution is currently blocked even when wording is supplied, because the renderer/caption does not yet inject attribution. Such an asset cannot pass until that capability is implemented and tested.
- The Pro renderer now consumes the exact local rights-cleared background/audio files; it no longer downloads a background URL during rendering. Candidate preview delivery independently rechecks the same rights records.
- These checks validate the recorded evidence and exact file identity; they do not independently adjudicate the legal meaning or authenticity of a license. Human review remains mandatory.


## 7. Additional discovery source: Mixkit (reviewed 2026-11-07)

Mixkit may be used as an additional discovery source for Pro background video. The official Stock Video Free License states that items specifically marked with the **Free License** may be used in commercial and non-commercial projects, including social-media video posts, and may be downloaded, copied, modified, distributed, publicly performed, and broadcast without required attribution. The license also points to Mixkit User Terms for limitations.

- Official Free License: https://mixkit.co/license/modal/videoFree/
- User Terms: https://mixkit.co/terms/
- Example candidate page checked: https://mixkit.co/free-stock-video/beautiful-sunrise-landscape-1944/ (the page explicitly labels the free download as commercial/personal use under the Mixkit Stock Video Free License).
- Example second candidate page checked: https://mixkit.co/free-stock-video/forest-during-the-morning-3012/ (same explicit Free License indication).

**Important:** Mixkit also lists Restricted License items. A free download is not by itself enough: the exact asset page must explicitly identify the applicable Free License, not Restricted License. This provider-level license review does not establish that an exact downloaded file has no third-party rights issues. The existing per-asset file/hash, source/creator/owner, territory/validity, intended-use, attribution, and third-party review gates remain mandatory. These example candidates are research leads only and are not approved media.


### Mixkit User Terms caveats (checked 2026-11-07)

The Mixkit User Terms (last revised 2025-10-02) state that downloading an Item grants a non-exclusive license, not ownership; prohibit scripts/bots used for mass downloads or scraping the library; and warn that some Item components (for example, trademarks or brands) may be third-party material not cleared for the user's use. Therefore Pro must not scrape or bulk-download Mixkit. Any acquisition must use the provider's ordinary permitted individual download flow, and the exact downloaded file still needs human inspection and per-asset rights review. Source: https://mixkit.co/terms/.
