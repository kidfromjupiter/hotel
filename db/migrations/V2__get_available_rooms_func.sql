create or replace function get_available_rooms(p_check_in DATE, p_check_out DATE, p_branch TEXT, p_children INTEGER , p_adults INTEGER)
returns JSONB
language plpgsql
as $$
declare 
  result JSONB;
begin
  select coalesce(
    jsonb_agg(to_jsonb(r)),
    '[]'::JSONB
  )
  into result 
  from room_details r
  join branches b
  on r.branch_id = b.branch_id
  where b.branch_name = p_branch and 
  not exists (
    select 1 
    from booking bk
    where bk.room_number = r.room_number
      and bk.branch_id = r.branch_id
      and bk.start_date < p_check_out
      and bk.end_date > p_check_in
  );

  return result;

end;
$$;
