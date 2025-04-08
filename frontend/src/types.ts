export interface User {
  username: string;
  role: string;
}

export interface Asset {
  asset_tag: string;
  user_id?: string;
  user_name?: string;
  department?: string;
  location?: string;
  date_of_return?: string;
  date_of_reassign?: string;
  _source_table?: string;
}

export interface ReassignmentData {
  user_id?: string;
  user_name?: string;
  department?: string;
  location?: string;
  date_of_return?: string;
  date_of_reassign?: string;
}