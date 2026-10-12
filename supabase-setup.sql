-- 숫자숲 탐험대: 태블릿 기록 맞추기용 저장소
-- Supabase 대시보드 → SQL Editor → New query → 이 내용을 통째로 붙여 넣고 Run
-- 표(nf_sync)는 직접 읽고 쓸 수 없게 막고, 아래 두 함수로만 접근합니다.
-- 가족 코드는 저장하지 않고, 코드의 지문(sha256 해시)만 저장합니다.

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.nf_sync (
  code_hash  text primary key,
  data       jsonb not null,
  rev        bigint not null default 0,
  updated_at timestamptz not null default now()
);

alter table public.nf_sync enable row level security;
revoke all on public.nf_sync from anon, authenticated;

-- 기록 가져오기
create or replace function public.nf_get(p_code text)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  h text;
  r record;
begin
  if p_code is null or length(p_code) < 8 then
    raise exception 'family code too short';
  end if;
  h := encode(digest(p_code, 'sha256'), 'hex');
  select data, rev into r from public.nf_sync where code_hash = h;
  if not found then
    return null;
  end if;
  return jsonb_build_object('data', r.data, 'rev', r.rev);
end;
$$;

-- 기록 올리기: 서버 기록 번호가 p_base와 같을 때만 저장 (다른 태블릿이 먼저 바꿨으면 -1)
create or replace function public.nf_put(p_code text, p_data jsonb, p_rev bigint, p_base bigint)
returns bigint
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  h text;
  cur bigint;
begin
  if p_code is null or length(p_code) < 8 then
    raise exception 'family code too short';
  end if;
  if octet_length(p_data::text) > 3000000 then
    raise exception 'data too big';
  end if;
  h := encode(digest(p_code, 'sha256'), 'hex');
  select rev into cur from public.nf_sync where code_hash = h for update;
  if not found then
    insert into public.nf_sync(code_hash, data, rev, updated_at) values (h, p_data, p_rev, now());
    return p_rev;
  end if;
  if cur <> p_base then
    return -1;
  end if;
  update public.nf_sync set data = p_data, rev = p_rev, updated_at = now() where code_hash = h;
  return p_rev;
end;
$$;

revoke all on function public.nf_get(text) from public;
revoke all on function public.nf_put(text, jsonb, bigint, bigint) from public;
grant execute on function public.nf_get(text) to anon, authenticated;
grant execute on function public.nf_put(text, jsonb, bigint, bigint) to anon, authenticated;
