#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re
import time
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

def get_version():
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, "version_info.txt")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"StringStruct\(u'ProductVersion',\s*u'([^']+)'\)", content)
                if match:
                    return match.group(1)
        
        return "0.0.0"
    except Exception:
        return "未知版本"

def show_muse_banner():
    banner = r"""
          _____                    _____                    _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \         
        /::\____\                /::\____\                /::\    \                /::\    \        
       /::::|   |               /:::/    /               /::::\    \              /::::\    \       
      /:::::|   |              /:::/    /               /::::::\    \            /::::::\    \      
     /::::::|   |             /:::/    /               /:::/\:::\    \          /:::/\:::\    \     
    /:::/|::|   |            /:::/    /               /:::/__\:::\    \        /:::/__\:::\    \    
   /:::/ |::|   |           /:::/    /                \:::\   \:::\    \      /::::\   \:::\    \   
  /:::/  |::|___|______    /:::/    /      _____    ___\:::\   \:::\    \    /::::::\   \:::\    \  
 /:::/   |::::::::\    \  /:::/____/      /\    \  /\   \:::\   \:::\    \  /:::/\:::\   \:::\    \ 
/:::/    |:::::::::\____\|:::|    /      /::\____\/::\   \:::\   \:::\____\/:::/__\:::\   \:::\____\
\::/    / ~~~~~/:::/    /|:::|____\     /:::/    /\:::\   \:::\   \::/    /\:::\   \:::\   \::/    /
 \/____/      /:::/    /  \:::\    \   /:::/    /  \:::\   \:::\   \/____/  \:::\   \:::\   \/____/ 
             /:::/    /    \:::\    \ /:::/    /    \:::\   \:::\    \       \:::\   \:::\    \     
            /:::/    /      \:::\    /:::/    /      \:::\   \:::\____\       \:::\   \:::\____\    
           /:::/    /        \:::\__/:::/    /        \:::\  /:::/    /        \:::\   \::/    /    
          /:::/    /          \::::::::/    /          \:::\/:::/    /          \:::\   \/____/     
         /:::/    /            \::::::/    /            \::::::/    /            \:::\    \         
        /:::/    /              \::::/    /              \::::/    /              \:::\____\        
        \::/    /                \::/____/                \::/    /                \::/    /        
         \/____/                  ~~                       \/____/                  \/____/         
    """
    print(banner)
    print()
    version = get_version()
    print(f"MUSE-UCAS-Searcher v{version}")
    print("=" * 88)
    print()

@dataclass
class CourseInfo:
    course_name: str
    university_name: str
    degree: str
    duration: str
    entry_requirements: str
    a_level_requirement: Optional[str]
    ucas_tariff_points: Optional[int]
    course_link: str
    raw_a_level_offer: str = ""

class UCASSearcher:
    
    def __init__(self):
        self.base_url = "https://services.ucas.com/search/api/v2/courses/search"
        self.params = "fields=courses(id,academicYearId,applicationCode,subjects(caption),courseTitle,routingData(destination(caption),scheme(caption)),provider(id,name,logoUrl,providerSort,institutionCode),options(id,outcomeQualification(caption),duration,durationRange(min,max),studyMode,startDate,location,academicEntryRequirements(qualifications,ucasTariffPointsMin,ucasTariffPointsMax,ucasTariffPointsDisplayMin,ucasTariffPointsDisplayMax),features)),information(postcodeLookup,courseCounts(perProviderCourseCountsByDestination,totalCourseCount,totalProviderCount,ucasTeacherTrainingProvider,degreeApprenticeship,higherTechnicalQualifications,providers,schemes,subjects,startDates,studyTypes,attendanceTypes,acceleratedDegrees,qualifications,entryPoints,allFilters),paging)"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_courses(self, keyword: str, page_size: int = 50) -> List[Dict[str, Any]]:
        all_courses = []
        page_number = 1
        
        while True:
            payload = {
                "searchTerm": keyword,
                "filters": {
                    "academicYearId": "2026",
                    "destinations": ["Undergraduate"],
                    "providers": [],
                    "schemes": [],
                    "ucasTeacherTrainingProvider": False,
                    "degreeApprenticeship": False,
                    "studyTypes": [],
                    "subjects": [],
                    "qualifications": [],
                    "attendanceTypes": [],
                    "acceleratedDegrees": False,
                    "entryPoint": None,
                    "regions": [],
                    "vacancy": "",
                    "startDates": [],
                    "higherTechnicalQualifications": False
                },
                "options": {
                    "sort": [],
                    "paging": {
                        "pageNumber": page_number,
                        "pageSize": page_size
                    },
                    "viewType": "course"
                },
                "inClearing": False
            }
            
            try:
                response = self.session.post(f"{self.base_url}?{self.params}", json=payload)
                response.raise_for_status()
                data = response.json()
                
                courses = data.get('courses', [])
                if not courses:
                    break
                    
                all_courses.extend(courses)
                print(f"已获取第{page_number}页，共{len(courses)}个课程")
                
                total_count = data.get('information', {}).get('courseCounts', {}).get('totalCourseCount', 0)
                if len(all_courses) >= total_count:
                    break
                    
                page_number += 1
                time.sleep(1)
                
            except requests.RequestException as e:
                print(f"请求错误: {e}")
                time.sleep(3)
                break
            except Exception as e:
                print(f"解析错误: {e}")
                break
        
        print(f"总共获取到{len(all_courses)}个课程")
        return all_courses
    
    def parse_a_level_grade(self, offer: str) -> int:
        if not offer:
            return 0
            
        grade_values = {'A*': 4, 'A': 3, 'B': 2, 'C': 1, 'D': 0}
        
        if ' - ' in offer:
            offer = offer.split(' - ')[0]
        
        clean_offer = re.sub(r'[^A*ABCD]', '', offer)
        
        total_score = 0
        i = 0
        while i < len(clean_offer):
            if i < len(clean_offer) - 1 and clean_offer[i:i+2] == 'A*':
                total_score += grade_values['A*']
                i += 2
            elif clean_offer[i] in grade_values:
                total_score += grade_values[clean_offer[i]]
                i += 1
            else:
                i += 1
        
        return total_score
    
    def extract_course_info(self, course_data: Dict[str, Any]) -> List[CourseInfo]:
        course_infos = []
        
        course_id = course_data.get('id', '')
        course_title = course_data.get('courseTitle', '')
        provider = course_data.get('provider', {})
        university_name = provider.get('name', '')
        
        options = course_data.get('options', [])
        
        for option in options:
            outcome_qualification = option.get('outcomeQualification', {})
            degree = outcome_qualification.get('caption', '')
            
            duration_info = option.get('duration') or {}
            duration_quantity = duration_info.get('quantity', 0) if duration_info else 0
            duration_type_info = duration_info.get('durationType') or {} if duration_info else {}
            duration_type = duration_type_info.get('caption', '') if duration_type_info else ''
            duration = f"{duration_quantity} {duration_type}" if duration_quantity else ''
            
            entry_requirements = option.get('academicEntryRequirements', {})
            qualifications = entry_requirements.get('qualifications', [])
            
            a_level_requirement = None
            a_level_offer = ""
            for qual in qualifications:
                if qual.get('qualificationName') == 'A level':
                    summary = qual.get('summary', {})
                    a_level_offer = summary.get('offer', '')
                    a_level_requirement = f"A Level: {a_level_offer}"
                    if summary.get('requirements'):
                        a_level_requirement += f" ({summary.get('requirements')})"
                    break
            
            ucas_tariff_points = entry_requirements.get('ucasTariffPointsMin')
            
            requirements_text = []
            for qual in qualifications:
                if not qual.get('notAccepted', False):
                    qual_name = qual.get('qualificationName', '')
                    summary = qual.get('summary', {})
                    offer = summary.get('offer', '')
                    requirements = summary.get('requirements', '')
                    
                    if offer or requirements:
                        req_text = f"{qual_name}: {offer}"
                        if requirements:
                            req_text += f" ({requirements})"
                        requirements_text.append(req_text)
            
            entry_requirements_str = '; '.join(requirements_text)
            
            course_link = f"https://digital.ucas.com/coursedisplay/courses/{course_id}?academicYearId=2026"
            
            course_info = CourseInfo(
                course_name=course_title,
                university_name=university_name,
                degree=degree,
                duration=duration,
                entry_requirements=entry_requirements_str,
                a_level_requirement=a_level_requirement,
                ucas_tariff_points=ucas_tariff_points,
                course_link=course_link,
                raw_a_level_offer=a_level_offer
            )
            
            course_infos.append(course_info)
        
        return course_infos
    
    def sort_courses_by_a_level(self, courses: List[CourseInfo]) -> List[CourseInfo]:
        return sorted(courses, key=lambda x: self.parse_a_level_grade(x.raw_a_level_offer), reverse=True)
    
    def sort_courses_by_ucas_tariff(self, courses: List[CourseInfo]) -> List[CourseInfo]:
        return sorted(courses, key=lambda x: x.ucas_tariff_points or 0, reverse=True)
    
    def save_to_json(self, courses: List[CourseInfo], filename: str):
        courses_data = []
        for course in courses:
            course_dict = {
                "专业名": course.course_name,
                "学校名": course.university_name,
                "学位": course.degree,
                "学习时长": course.duration,
                "录取要求": course.entry_requirements,
                "A Level要求": course.a_level_requirement,
                "UCAS Tariff分数": course.ucas_tariff_points,
                "链接": course.course_link
            }
            courses_data.append(course_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(courses_data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存{len(courses_data)}个课程到 {filename}")

def main():
    show_muse_banner()
    searcher = UCASSearcher()
    
    keyword = input("请输入搜索关键词: ").strip()
    if not keyword:
        print("关键词不能为空")
        return
    
    print(f"正在搜索关键词: {keyword}")
    
    raw_courses = searcher.search_courses(keyword)
    if not raw_courses:
        print("未找到相关课程")
        return
    
    all_courses = []
    for i, course_data in enumerate(raw_courses):
        try:
            course_infos = searcher.extract_course_info(course_data)
            all_courses.extend(course_infos)
        except Exception as e:
            print(f"解析第{i+1}个课程时出错: {e}")
            continue
    
    print(f"解析得到{len(all_courses)}个课程选项")
    
    courses_with_a_level = []
    courses_without_a_level = []
    
    for course in all_courses:
        if course.a_level_requirement and course.raw_a_level_offer:
            courses_with_a_level.append(course)
        else:
            courses_without_a_level.append(course)
    
    print(f"有A Level要求的课程: {len(courses_with_a_level)}个")
    print(f"没有A Level要求的课程: {len(courses_without_a_level)}个")
    
    if courses_with_a_level:
        sorted_a_level_courses = searcher.sort_courses_by_a_level(courses_with_a_level)
        filename_a_level = f"{keyword}_a_level_sorted.json"
        searcher.save_to_json(sorted_a_level_courses, filename_a_level)
        
        print("\n前5个A Level要求最高的课程:")
        for i, course in enumerate(sorted_a_level_courses[:5], 1):
            print(f"{i}. {course.course_name} - {course.university_name} (A Level: {course.raw_a_level_offer})")
    
    if courses_without_a_level:
        sorted_tariff_courses = searcher.sort_courses_by_ucas_tariff(courses_without_a_level)
        filename_tariff = f"{keyword}_ucas_tariff_sorted.json"
        searcher.save_to_json(sorted_tariff_courses, filename_tariff)
        
        print("\n前5个UCAS Tariff分数最高的课程:")
        for i, course in enumerate(sorted_tariff_courses[:5], 1):
            tariff_points = course.ucas_tariff_points or 0
            print(f"{i}. {course.course_name} - {course.university_name} (UCAS Tariff: {tariff_points}分)")
    
    print("\n搜索完成！")

def run_main():
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\n程序已被用户中断")
        except Exception as e:
            import traceback
            print(f"程序运行出错: {e}")
            print("\n完整错误详情:")
            print(traceback.format_exc())
        
        while True:
            choice = input("\n退出(T)/重新开始(S): ").strip().upper()
            if choice == 'T':
                print("程序已退出")
                return
            elif choice == 'S':
                print("\n重新开始程序...\n")
                break
            else:
                print("请输入 T 或 S")

if __name__ == "__main__":
    run_main()