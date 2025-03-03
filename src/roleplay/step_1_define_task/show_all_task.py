################################
#统计指定目录下不同字母开头的.json文件的数量，并返回一个字典。
import os
def count_json_by_letter(src_directory):
    # 初始化字母计数字典和文件总数计数器
    count_dict = {}
    total_files = 0
    # 遍历指定目录
    for filename in os.listdir(src_directory):
        # 检查是否为json文件
        if filename.lower().endswith('.json'):
            # 增加文件总数计数器
            total_files += 1
            # 获取文件名第一个字母
            first_letter = filename.split(".")[0]
            # 统计该字母开头的json文件数量
            if first_letter in count_dict:
                count_dict[first_letter] += 1
            else:
                count_dict[first_letter] = 1
    # 返回字母计数字典和文件总数
    return count_dict, total_files

# 使用示例
src_directory = '/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_1_define_task/define_finish' # 替换为实际的目录路径
letter_counts, total_count = count_json_by_letter(src_directory)
print("Letter counts:", letter_counts)
print("Total JSON files:", total_count)

print(f"task names:\n{list(letter_counts.keys())}")
# ['scholarism-conference_invitation', 'courier-delayed_package_handling', 'travel-booking', 'bank-activate_bank_card', 'white_goods-repair_appointment', 'shopping-sams_club_member_day_invitation', 'education-online_market', 'workplace-apply_for_workcard', 'photo_studio-photo_appointment', 'hospital-vaccine_inform', 'airport-check_in', 'shopping-redeem_promotion', 'cosmetology-product_follow_up', 'health_preservationhot-product_promotion', 'household-unblocking_pipeline', 'restaurant-private_room_booking', 'cinema-movie_ticket_purchase', 'pet-complain_consult', 'hotel-check_in', 'entertainment-ktv_complain_consult', 'gym-private_tuoring', 'car_insurance-sales_promotion', 'cosmetology-member_day', 'pet-adoption_facilitation', 'community-competition', 'restaurant-private_room_reservation', 'library-borrow_book', 'health-blood_pressure_monitoring', 'telecom-activate_package', 'household-moving_appointment', 'hospital-appointment', 'domestic_service-complain', 'shopping-take_out_order', 'school-home_visit_appointment', 'gym-swimming_pass_promotion', 'shopping-return_request', 'white_goods-installation_appointment', 'real_estate-event_invitation', 'school-reissue_student_card', 'internet-broadband_repair_phone_support', 'bank-agent_large_transaction_inquiry', 'glasses-fitting', 'school-archive_uery', 'bank-financial_product_sales', 'computer-repair_appointment', 'household-property_fee_deposit', 'bank-golf_invitation', 'account-password_recovery', 'survey-membership_reward', 'telecom-sim_card_upgrade_promotion', 'telecom-broadband_upgrade', 'household-recycling_appointment', 'bank-loan_followup', 'community-lost_and_found']